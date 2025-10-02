from aiogram import Router

from . import common, stats, settings, feedback, misc, pet


def setup_handlers() -> Router:
    router = Router()
    router.include_router(common.router)
    router.include_router(stats.router)
    router.include_router(settings.router)
    router.include_router(feedback.router)
    router.include_router(pet.router)
    router.include_router(misc.router)
    return router


__all__ = ["setup_handlers"]