from db.models import Agent, User, BusinessArea

def retrieve_data(db, type: str, ids: list = None, user_id: int = None) -> list:
    type_mappings = {
        "agents": {
            "model": Agent,
            "filter": lambda id: Agent.id == id,
            "fields": lambda entity: {
                "id": entity.id,
                "name": entity.name,
                "personality": entity.personality,
            },
        },
        "team_members": {
            "model": User,
            "filter": lambda id: (User.id == id) & (User.role_id == 7),
            "fields": lambda entity: {
                "id": entity.id,
                "name": entity.name,
                "role": entity.type,
                "rating": float(entity.rating),
            },
        },
        "clients": {
            "model": User,
            "filter": lambda id: (User.id == id) & (User.role_id == 6),
            "fields": lambda entity: {
                "id": entity.id,
                "name": entity.name,
                "description": entity.description,
            },
        },
        "respondents": {
            "model": User,
            "filter": lambda id: (User.id == id) & (User.role_id == 5),
            "fields": lambda entity: {
                "id": entity.id,
                "name": entity.name,
                "description": entity.description,
                "incentive_type": entity.incentive_type,
                "rating": float(entity.rating)
            },
        },
        "business_area": {
             "model": BusinessArea,
            "filter": lambda user_id: BusinessArea.created_by == user_id,
            "fields": lambda entity: {
                "id": entity.id,
                "name": entity.name,
            },
        }
    }

    if type not in type_mappings:
        return []

    config = type_mappings[type]
    data = {f"{type}":[]}

    if type == "business_area" and user_id is not None:
        entities = db.query(config["model"]).filter(config["filter"](user_id)).all()
        for entity in entities:
            data[type].append(config["fields"](entity))
    else:
        for id in ids:
            entity = db.query(config["model"]).filter(config["filter"](id)).first()
            if entity:
                data[type].append(config["fields"](entity))

    return data
