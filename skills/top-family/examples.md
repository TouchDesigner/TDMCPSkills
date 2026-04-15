# TOP Examples

## Feedback Loop
constantTOP (clear) → feedbackTOP → [processing] → nullTOP (loop back automatic)
- feedbackTOP `top` par = downstream null that closes the loop
- Set `format=rgba32float` for data/HDR
- feedbackTOP = 1 iteration per frame. Use `npasses` on glslmultiTOP for iterative solvers
- Close the loop before compiling shaders that depend on it

## Color Correction Chain
`sourceTOP → levelTOP (contrast/gamma) → hsvTOP (saturation) → nullTOP`

## Composite Layers
`backgroundTOP → compositeTOP ← foregroundTOP`
Note: input 0 = foreground (on top), input 1 = background. Opposite of Photoshop.

## Post-Processing
`renderTOP → glslmultiTOP (bloom) → glslmultiTOP (tonemap) → nullTOP`
Each glslmultiTOP reads input via `sTD2DInputs[0]` at `vUV.st`.

## Depth Buffer Setup
`renderTOP → depthTOP (pixelformat=rgba16float, depthspace=reranged) → nullTOP`
Produces usable 0-1 depth values.

## Cross-COMP Reference
`selectTOP` with expression: `parent.Project.op('Core/Render/out1').path`
Use parent shortcuts, never relative paths.
