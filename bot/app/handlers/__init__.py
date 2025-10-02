from aiogram import Router


def setup_handlers() -> Router:
    from . import common, stats, settings, feedback, misc, pet
    from ..keyboards import webapp

    router = Router()
    router.include_router(common.router)
    router.include_router(stats.router)
    router.include_router(settings.router)
    router.include_router(feedback.router)
    router.include_router(pet.router)
    router.include_router(webapp.router)
    router.include_router(misc.router)
    return router


__all__ = ["setup_handlers"]