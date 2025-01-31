from pymongo.collection import Collection
import logging

# Returns true an entry (match) within the table with provided field already exists
def search_user_db(collection: Collection, field: str, match: str) -> bool:
    try:
        ret = collection.find_one({field: match})
        logging.info(f"search_user_db: found {ret}")
        return True, ret
    except:
        logging.critical("search_user_db: could not search for the user")
        return False, 0 



