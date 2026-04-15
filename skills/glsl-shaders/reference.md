# GLSL Reference — Built-in Uniforms & Functions

## TOP Uniforms

```glsl
uniform sampler2D sTD2DInputs[TD_NUM_2D_INPUTS];
uniform sampler3D sTD3DInputs[TD_NUM_3D_INPUTS];
uniform sampler2DArray sTD2DArrayInputs[TD_NUM_2D_ARRAY_INPUTS];
uniform samplerCube sTDCubeInputs[TD_NUM_CUBE_INPUTS];
uniform TDTexInfo uTD2DInfos[TD_NUM_2D_INPUTS];  // .res = (1/w, 1/h, w, h)
uniform TDTexInfo uTDOutputInfo;
uniform sampler2D sTDNoiseMap;     // 256x256 random
uniform sampler1D sTDSineLookup;
uniform int uTDPass;               // current pass (0-based)
uniform int uTDCurrentDepth;       // current Z slice for 3D textures
in vec2 vUV;                       // texture coords (0-1), only without custom vertex shader
```

Sampler indexing is **per-type**, not per-connector. 2D/3D/cube inputs each have separate arrays.

## TOP Functions

```glsl
vec4 TDOutputSwizzle(vec4 c);                           // REQUIRED on all pixel outputs
void TDImageStoreOutput(uint idx, ivec3 coord, vec4 c); // compute output (auto-swizzles)
vec4 TDImageLoadOutput(uint idx, ivec3 coord);           // compute readback
float TDPerlinNoise(vec2/vec3/vec4 v);                   // [-1,1] — NOT in POP
float TDSimplexNoise(vec2/vec3/vec4 v);                  // [-1,1] — NOT in POP
vec3 TDHSVToRGB(vec3 c);
vec3 TDRGBToHSV(vec3 c);
mat3 TDRotateOnAxis(float rad, vec3 axis);
mat3 TDRotateX/Y/Z(float rad);
vec4 TDDither(vec4 color);
```

## MAT Uniforms

```glsl
uniform TDMatrix uTDMats[TD_NUM_CAMERAS];       // world, cam, proj matrices
uniform TDCameraInfo uTDCamInfos[TD_NUM_CAMERAS]; // nearFar, fog
uniform TDLight uTDLights[TD_NUM_LIGHTS];        // position, direction, diffuse, shadow
uniform TDEnvLight uTDEnvLights[TD_NUM_ENV_LIGHTS];
uniform TDGeneral uTDGeneral;                    // ambientColor, viewport
```

## MAT Vertex Functions

```glsl
vec4 TDDeform(vec3 pos);           // pos → world space (instancing, deformation)
vec3 TDDeformNorm(vec3 n);         // normal → world space
vec4 TDWorldToProj(vec4 worldPos); // world → clip (ALWAYS for gl_Position)
int  TDCameraIndex();              // pass as flat varying to pixel shader
vec4 TDPointColor();               // vertex color
vec4 TDInstanceColor(vec4 c);      // apply instance tint
vec3 TDPos();                      // raw vertex position
vec3 TDNormal();                   // raw normal
```

## MAT Pixel Functions

```glsl
TDPBRResult TDLightingPBR(int idx, vec3 diff, vec3 spec, vec3 pos, vec3 norm,
    float shadowStr, vec3 shadowCol, vec3 viewDir, float roughness);
TDPBRResult TDEnvLightingPBR(inout vec3 diff, inout vec3 spec, int idx,
    vec3 diffCol, vec3 specCol, vec3 norm, vec3 viewDir, float rough, float ao);
void  TDCheckDiscard();
vec4  TDOutputSwizzle(vec4 c);     // REQUIRED
vec4  TDDither(vec4 c);
vec4  TDFog(vec4 c, vec3 worldPos, int camIdx);
```

## MAT Compile-Time Defines

```glsl
TD_VERTEX_SHADER / TD_PIXEL_SHADER / TD_GEOMETRY_SHADER / TD_COMPUTE_SHADER
TD_NUM_LIGHTS / TD_NUM_ENV_LIGHTS / TD_NUM_CAMERAS / TD_NUM_COLOR_BUFFERS
```

## POP Buffer Access (in TOP shaders)

Set `buffer0pop`, `buffer0attr`, `buffer0name` on glslmultiTOP:
```glsl
vec4 TDBuffer_<Name>(uint elemIdx);              // read attribute by index
vec4 TDBuffer_<Name>(uint elemIdx, uint arrIdx); // array attribute element
```

## POP Attributes (in MAT vertex shaders)

Declare on Attributes page: `attr0name=Colors`, `attr0type=float4`:
```glsl
vec4 TDAttrib_<Name>(int arrayIdx);  // per-vertex, auto-indexed
```

## Multi-Pass (npasses)

`npasses=N` runs shader N times per frame. On pass 2+, input 0 is replaced with previous pass output (automatic ping-pong). Other inputs unchanged. Ideal for iterative solvers.

## 3D Texture Output

`type=texture3d`, `depth=custom`, `customdepth=N`. Shader runs per Z slice. Use `uTDCurrentDepth` for Z index. Use `sTD3DInputs[]` for 3D input sampling.

## Multiple Render Targets (glslmultiTOP)

```glsl
layout(location = 0) out vec4 oFragColor[TD_NUM_COLOR_BUFFERS];
```
Set `numcolorbufs` on operator. Use `renderselectTOP` to split outputs downstream.

## Template: Minimal Pixel Shader

```glsl
layout(location = 0) out vec4 fragColor;
void main() {
    vec4 color = texture(sTD2DInputs[0], vUV.st);
    fragColor = TDOutputSwizzle(color);
}
```

## Template: Minimal glslMAT (Combined DAT)

```glsl
#ifdef TD_VERTEX_SHADER
out Vert { vec4 color; vec3 worldPos; vec3 worldNorm; flat int cameraIndex; } oVert;
void main() {
    oVert.color = TDInstanceColor(TDPointColor());
    vec4 worldPos = TDDeform(TDPos());
    oVert.worldPos = worldPos.xyz;
    oVert.worldNorm = TDDeformNorm(TDNormal());
    oVert.cameraIndex = TDCameraIndex();
    gl_Position = TDWorldToProj(worldPos);
}
#endif
#ifdef TD_PIXEL_SHADER
in Vert { vec4 color; vec3 worldPos; vec3 worldNorm; flat int cameraIndex; } iVert;
layout(location = 0) out vec4 oFragColor[TD_NUM_COLOR_BUFFERS];
void main() {
    TDCheckDiscard();
    vec3 norm = normalize(iVert.worldNorm);
    vec3 camPos = uTDMats[iVert.cameraIndex].camInverse[3].xyz;
    vec3 viewDir = normalize(camPos - iVert.worldPos);
    vec3 diffuse = vec3(0.0); vec3 specular = vec3(0.0);
    for (int i = 0; i < TD_NUM_LIGHTS; i++) {
        TDPBRResult res = TDLightingPBR(i, iVert.color.rgb, vec3(0.04),
            iVert.worldPos, norm, 1.0, vec3(0.0), viewDir, 0.5);
        diffuse += res.diffuse; specular += res.specular;
    }
    for (int i = 0; i < TD_NUM_ENV_LIGHTS; i++) {
        TDEnvLightingPBR(diffuse, specular, i, iVert.color.rgb, vec3(0.04),
            norm, viewDir, 0.5, 1.0);
    }
    oFragColor[0] = TDOutputSwizzle(TDDither(vec4(diffuse + specular, iVert.color.a)));
}
#endif
```
