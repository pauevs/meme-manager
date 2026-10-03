from typing import List, Optional


class Meme:
    """Базовый класс мема."""

    def __init__(self, id: Optional[int] = None,
                 title: str = "",
                 description: str = ""):
        self.id = id
        self.title = self._validate_str(title, "title")
        self.description = self._validate_str(description, "description")

    @staticmethod
    def _validate_str(value, field):
        if not isinstance(value, str):
            raise ValueError(f"{field} должен быть строкой")
        return value

    def __eq__(self, other):
        if not isinstance(other, Meme):
            return False
        return (self.id == other.id
                and self.title == other.title
                and self.description == other.description)

    def __hash__(self):
        return hash((self.id, self.title, self.description))

    def __repr__(self):
        return (f"Meme(id={self.id}, title={self.title!r}, "
                f"description={self.description!r})")

    def __str__(self):
        return f"[Meme #{self.id}] {self.title} — {self.description}"


class TextMeme(Meme):
    """Текстовый мем (с текстом и шрифтом)."""

    def __init__(self, id=None, title="", description="",
                 text_content="", font_size=14):
        super().__init__(id, title, description)
        self.text_content = self._validate_str(text_content, "text_content")
        self.font_size = self._validate_font_size(font_size)

    @staticmethod
    def _validate_font_size(value):
        if not isinstance(value, int):
            raise ValueError("font_size должен быть целым числом")
        if not (8 <= value <= 72):
            raise ValueError("font_size должен быть в диапазоне от 8 до 72")
        return value

    def __eq__(self, other):
        if not isinstance(other, TextMeme):
            return False
        return (super().__eq__(other)
                and self.text_content == other.text_content
                and self.font_size == other.font_size)

    def __hash__(self):
        return hash((super().__hash__(), self.text_content, self.font_size))

    def __repr__(self):
        return (f"TextMeme(id={self.id}, title={self.title!r}, "
                f"font_size={self.font_size})")


class ImageMeme(Meme):
    """Мем-картинка."""

    def __init__(self, id=None, title="", description="",
                 image_path="", width=300):
        super().__init__(id, title, description)
        self.image_path = self._validate_str(image_path, "image_path")
        self.width = self._validate_width(width)

    @staticmethod
    def _validate_width(value):
        if not isinstance(value, int):
            raise ValueError("width должен быть целым числом")
        if not (50 <= value <= 4000):
            raise ValueError("width должен быть в диапазоне от 50 до 4000")
        return value

    def __eq__(self, other):
        if not isinstance(other, ImageMeme):
            return False
        return (super().__eq__(other)
                and self.image_path == other.image_path
                and self.width == other.width)

    def __hash__(self):
        return hash((super().__hash__(), self.image_path, self.width))

    def __repr__(self):
        return (f"ImageMeme(id={self.id}, title={self.title!r}, "
                f"width={self.width})")


class VideoMeme(Meme):
    """Мем-видео."""

    def __init__(self, id=None, title="", description="",
                 video_path="", duration_sec=10):
        super().__init__(id, title, description)
        self.video_path = self._validate_str(video_path, "video_path")
        self.duration_sec = self._validate_duration(duration_sec)

    @staticmethod
    def _validate_duration(value):
        if not isinstance(value, int):
            raise ValueError("duration_sec должен быть целым числом")
        if not (1 <= value <= 600):
            raise ValueError("duration_sec должен быть в диапазоне от 1 до 600")
        return value

    def __eq__(self, other):
        if not isinstance(other, VideoMeme):
            return False
        return (super().__eq__(other)
                and self.video_path == other.video_path
                and self.duration_sec == other.duration_sec)

    def __hash__(self):
        return hash((super().__hash__(), self.video_path, self.duration_sec))

    def __repr__(self):
        return (f"VideoMeme(id={self.id}, title={self.title!r}, "
                f"duration_sec={self.duration_sec})")


class Tag:
    """Тег для мемов."""

    def __init__(self, id: Optional[int] = None,
                 name: str = "",
                 description: Optional[str] = None):
        self.id = id
        self.name = name
        self.description = description

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return False
        return (self.id == other.id
                and self.name == other.name
                and self.description == other.description)

    def __hash__(self):
        return hash((self.id, self.name, self.description))

    def __repr__(self):
        return f"Tag(id={self.id}, name={self.name!r})"