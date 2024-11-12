from .start import router as start_router
from .menu import router as menu_router
from .subscription import router as subscription_router
from .instruction import router as instruction_router
from .admin.stats import router as admin_stats_router
from .admin.camps import router as stats_router
from .admin.message import router as message_router
from .admin.admin_instruction import router as admin_instruction
from .admin.present import router as present_router
from .connect import router as connect_router
from .deactivation import router as deactivation_router

routers = [
    start_router,
    menu_router,
    subscription_router,
    instruction_router,
    admin_stats_router,
    stats_router,
    connect_router,
    admin_instruction,
    deactivation_router,
    message_router,
    present_router
]


def setup_routers(dp):
    for router in routers:
        dp.include_router(router)
