from typing import Optional,List


from pydantic import BaseModel, EmailStr


# Shared properties
class VideoBase(BaseModel):
    name: Optional[str] = None
    video_url: Optional[str] = None
    surface_plot_url: Optional[str] = None
    status:Optional[int] = None
    top:Optional[int] =None



# Properties to receive via API on creation
class VideoCreate(VideoBase):
    pass


# Properties to receive via API on update
class VideoUpdate(VideoBase):
    pass


class VideoInDBBase(VideoBase):
    id: Optional[int] = None
    create_time: Optional[str] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class Video(VideoInDBBase):
    pass

class VideoQuery(BaseModel):
    total:Optional[int]=0
    videos:List[Video]