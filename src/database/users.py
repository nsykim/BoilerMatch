from pymongo.collection import Collection

# Returns true an entry (match) within the table with provided field already exists
def search_user_db(collection: Collection, field: str, match: str) -> bool:
    return collection.find_one({field: match})

