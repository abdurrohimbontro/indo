import pymongo
from Kim.config import get_str_key

MONGO2 = get_str_key("FILTERS_MONGO", None)
MONGO = get_str_key("MONGO_URI", required=True)
if MONGO2 == None:
    MONGO2 = MONGO
myclient = pymongo.MongoClient(MONGO2)
mydb = myclient["polisi"]


async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    # mycol.create_index([('text', 'text')])

    data = {
        "text": str(text),
        "reply": str(reply_text),
        "btn": str(btn),
        "file": str(file),
        "alert": str(alert),
    }

    try:
        mycol.update_one({"text": str(text)}, {"$set": data}, upsert=True)
    except:
        print("Tidak dapat menyimpan, periksa db Anda")


async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]

    query = mycol.find({"text": name})
    # query = mycol.find( { "$text": {"$search": name}})
    try:
        for file in query:
            reply_text = file["reply"]
            btn = file["btn"]
            fileid = file["file"]
            try:
                alert = file["alert"]
            except:
                alert = None
        return reply_text, btn, alert, fileid
    except:
        return None, None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]

    texts = []
    query = mycol.find()
    try:
        for file in query:
            text = file["text"]
            texts.append(text)
    except:
        pass
    return texts


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]

    myquery = {"text": text}
    query = mycol.count_documents(myquery)
    if query == 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"'`{text}`'    dihapus. Saya tidak akan menanggapi filter itu lagi.",
            quote=True,
            parse_mode="md",
        )
    else:
        await message.reply_text("Tidak dapat menemukan filter itu!", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"Tidak ada yang perlu dihapus {title}!")
        return

    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"Semua filter dari {title} telah dihapus")
    except:
        await message.edit_text(f"Tidak dapat menghapus semua filter dari grup!")
        return


async def count_filters(group_id):
    mycol = mydb[str(group_id)]

    count = mycol.count()
    if count == 0:
        return False
    else:
        return count


async def filter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")
    if "USERS" in collections:
        collections.remove("USERS")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        count = mycol.count()
        totalcount = totalcount + count

    totalcollections = len(collections)

    return totalcollections, totalcount
