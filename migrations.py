async def m001_initial(db):
    """
    Initial donations table.
    """
    await db.execute(
        """
        CREATE TABLE donations.donations (
            id TEXT PRIMARY KEY,
            wallet TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        );
    """
    )