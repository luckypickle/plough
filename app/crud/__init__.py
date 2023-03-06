from .crud_order import order
from .crud_user import user
from .crud_mpcode import mpcode
from .crud_master import master
from .crud_product import product
from .crud_comment import comment
from .crud_version import version
from .crud_history import history
from .crud_favorite import favority
from .crud_invite import invite
from .crud_reward import reward
from .crud_withdraw import withdraw
from .crud_bill import bill
from .crud_master_product import masterProduct
from .crud_upload_history import upload_history
from .crud_video import video

from .crud_folder import folder
from .crud_folder_order import folder_order
from .crud_label import label
from .crud_history_event import history_event
from .crud_divination_settings import divination_settings
from .crud_history_combine import history_combine
# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
