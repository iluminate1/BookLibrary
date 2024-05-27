import urllib3
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class Link:
    title: Optional[str]
    url: Optional[str]


class Author:
    def __init__(
        self,
        name,
        fuller_name,
        birth_date,
        links,
        wikipedia,
        bio,
        photos,
    ) -> None:
        self.__name: str = name
        self.__full_name: str = fuller_name
        self.__birthdaty: str = birth_date
        self.__links: list[dict] = links
        self.__wikipedia: str = wikipedia
        self.__bio: str = bio
        self.__photos: list[int] = photos

    @property
    def name(self) -> str:
        return self.__name

    @property
    def full_name(self) -> str:
        return self.full_name

    @property
    def birthday(self) -> str:
        return self.__birthdaty

    @property
    def links(self) -> List[Dict]:
        return self.links

    @property
    def wikipedia(self) -> str:
        return self.__wikipedia

    @property
    def bio(self) -> str:
        return self.__bio

    @property
    def photo(self):
        return f"covers.openlibrary.org/a/id/{self.__photos[0]}-M.jpg"

    def get_ready_dict(self, photo_size: str = "L") -> dict[str, str | None]:
        if self.__photos:
            photo_url: str | None = (
                f"covers.openlibrary.org/a/id/{self.__photos[0]}-{photo_size}.jpg"
            )
        else:
            photo_url = None

        if self.__links:
            links: List[Link] | None = [
                Link(item.get("title"), item.get("url")) for item in self.__links
            ]
        else:
            links = None

        author_data = {
            "name": self.__name,
            "full_name": self.__full_name,
            "bio": self.__bio,
            "links": links,
            "birthday": self.__birthdaty,
            "wikipedia": self.__wikipedia,
            "photo": photo_url,
        }
        return author_data

    @staticmethod
    def get_author_from_json(data: dict[str, Any]) -> "Author":
        name = data.get("name", None)
        full_name = data.get("fuller_name", None)
        birthday = data.get("birth_date", None)
        links = data.get("links", None)
        wikipedia = data.get("wikipedia")
        bio = data.get("bio", None)
        photos = data.get("photos", None)

        return Author(
            name=name,
            fuller_name=full_name,
            birth_date=birthday,
            links=links,
            wikipedia=wikipedia,
            bio=bio,
            photos=photos,
        )

    def __repr__(self) -> str:
        return self.__name

    def __str__(self) -> str:
        return self.__name


class Book:
    def __init__(
        self,
        url,
        title,
        authors,
        publish_places,
        num_pages,
        publishers,
        publish_date,
        cover,
        preview,
    ) -> None:
        self.__url = url
        self.__title = title
        self.__authors = authors
        self.__publish_places = publish_places
        self.__num_pages = num_pages
        self.__publishers = publishers
        self.__publish_date = publish_date
        self.__cover = cover
        self.__preview = preview

    @property
    def url(self) -> str:
        return self.__url

    @property
    def title(self) -> str:
        return self.__title

    @property
    def authors(self):
        return self.__authors

    @property
    def publish_places(self) -> List[str]:
        return [item["name"] for item in self.__publish_places]

    @property
    def num_pages(self) -> int:
        return self.__num_pages

    @property
    def publishers(self) -> List[str]:
        return [item["name"] for item in self.__publishers]

    @property
    def publish_date(self) -> str:
        return self.__publish_date

    @property
    def cover(self) -> Dict[str, str]:
        return self.__cover

    @property
    def preview(self) -> str:
        return self.__preview[0].get("preview_url", None)

    def get_ready_dict(self):

        author_url: str = self.__authors[0].get("url", None)
        olid = author_url.split("/")[-2]

        author = API().get_author(olid=olid).get_ready_dict()

        if self.__publishers:
            publishers = [item["name"] for item in self.__publishers]
        else:
            publishers = None

        if self.__publish_places:
            publisher_place = [item["name"] for item in self.__publish_places]
        else:
            publisher_place = None

        default_preview_url: str = self.__preview[0].get("preview_url", None)
        embed_preview = default_preview_url.replace("/details/", "/embed/")

        response = urllib3.request(method="GET", url=self.__url, timeout=10)
        bs = BeautifulSoup(response.data, "lxml")
        container = bs.find("div", attrs={"class": "read-more__content"})

        desq = ""

        for p in container.findAll("p"):  # type: ignore
            desq += p.text.strip()

        try:
            language = bs.find("span", attrs={"itemprop": "inLanguage"})
            for a in language.findAll("a"):  # type: ignore
                lang = a.text.strip()
                break
        except:
            lang = None

        book_data = {
            "url": self.__url,
            "title": self.__title,
            "author": author,
            "num_pages": self.__num_pages,
            "publishers": publishers,
            "publish_place": publisher_place,
            "publish_date": self.__publish_date,
            "cover": self.__cover,
            "preview": {
                "embed": embed_preview,
                "external": self.__preview[0].get("preview_url", None),
            },
            "desq": desq,
            "lang": lang,
        }

        return book_data

    @staticmethod
    def get_book_from_json(data: Dict[str, Any]) -> "Book":
        url: str = data.get("url", None)
        title: str = data.get("title", None)
        authors: List[Dict[str, str]] = data.get("authors", None)
        publish_places: List[Dict[str, str]] = data.get("publish_places", None)
        num_pages: int = data.get("number_of_pages", None)
        publishers: List[Dict[str, str]] = data.get("publishers", None)
        publish_date: str = data.get("publish_date", None)
        cover: Dict[str, str] = data.get("cover", None)
        preview: List[Dict[str, str]] = data.get("ebooks", None)

        return Book(
            url=url,
            title=title,
            authors=authors,
            publish_places=publish_places,
            num_pages=num_pages,
            publishers=publishers,
            publish_date=publish_date,
            cover=cover,
            preview=preview,
        )

    def __repr__(self) -> str:
        return self.__title

    def __str__(self) -> str:
        return self.__title


class API:
    def __init__(self) -> None:
        self.base_url = "http://openlibrary.org/"

    def get_book(self, id: str, bibkey: str = "ISBN", jscmd: str = "data"):
        url = (
            f"{self.base_url}api/books?bibkeys={bibkey}:{id}&jscmd={jscmd}&format=json"
        )
        response = urllib3.request(method="GET", url=url, timeout=10)
        json_data = response.json()[f"{bibkey}:{id}"]
        return Book.get_book_from_json(json_data)

    def get_author(self, olid: str) -> Author:
        url = f"{self.base_url}authors/{olid}.json"
        response = urllib3.request(method="GET", url=url)
        json_data = response.json()
        return Author.get_author_from_json(json_data)
