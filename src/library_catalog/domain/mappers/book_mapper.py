"""Mapper для преобразования Book entity в DTO."""

from ...data.models.book import Book


class BookMapper:
    """Маппер для преобразования Book entity в DTO."""

    @staticmethod
    def to_show_book(book: Book):
        """
        Преобразовать Book ORM модель в ShowBook DTO.

        Args:
            book: ORM модель из БД

        Returns:
            ShowBook: Pydantic модель для API
        """
        from ...api.v1.schemas.book import ShowBook

        return ShowBook(
            book_id=book.book_id,
            title=book.title,
            author=book.author,
            year=book.year,
            genre=book.genre,
            pages=book.pages,
            available=book.available,
            isbn=book.isbn,
            description=book.description,
            extra=book.extra,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

    @staticmethod
    def to_show_books(books: list[Book]):
        """
        Преобразовать список книг.

        Args:
            books: Список ORM моделей

        Returns:
            Список ShowBook моделей
        """
        return [BookMapper.to_show_book(book) for book in books]