import torch
from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    EulerDiscreteScheduler,
    DPMSolverMultistepScheduler,
    LMSDiscreteScheduler
)

SCHEDULERS = {
    "Euler": EulerDiscreteScheduler,
    "DPM++": DPMSolverMultistepScheduler,
    "LMS": LMSDiscreteScheduler,
}

@torch.inference_mode()
def load_pipeline(model_id: str, img2img: bool = True, scheduler_name: str = "Euler"):
    scheduler_cls = SCHEDULERS.get(scheduler_name, EulerDiscreteScheduler)
    scheduler = scheduler_cls.from_pretrained(model_id, subfolder="scheduler")

    if img2img:
        pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            model_id,
            scheduler=scheduler,
            torch_dtype=torch.float16
        ).to("cuda")
    else:
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            scheduler=scheduler,
            torch_dtype=torch.float16
        ).to("cuda")
    return pipe

@torch.inference_mode()
def generate_image(pipe, prompt: str, negative_prompt: str = "", image=None,
                   strength: float = 0.55, guidance_scale: float = 7.5, steps: int = 50):
    if image is not None:
        return pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=image,
            strength=strength,
            guidance_scale=guidance_scale,
            num_inference_steps=steps
        ).images[0]
    else:
        return pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=steps
        ).images[0]
