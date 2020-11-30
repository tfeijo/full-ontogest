from flask import jsonify
from owlready2 import World, OwlReadyError
from src.utils.methods import Ontology, get_name_to_onto,\
clear_string,size_to_name_onto

class FarmController():
  
  def index():
    default_world = World(filename = "./src/ontology/db.sqlite3", exclusive=False)
    onto = default_world.get_ontology("./src/ontology/db.owl").load()
    
    query_farm = onto.Farm.instances()
    farms = []
    for farm in query_farm:
      farms.append(farm_to_json(farm))
    
    return jsonify(farms)

  def store(farm):
    try:
      db = Ontology(f'./src/ontology/db')
      db.load()
      city_name = f'{clear_string(farm["city"]["name"])}_{farm["city"]["state"]["uf"]}'
      state_name = f'{clear_string(farm["city"]["state"]["name"])}'
        
      
      with db.onto:
        device = db.onto.Device(farm['installation_id'])
        new = db.onto.Farm(f'{get_name_to_onto(device)}_{farm["id"]}')
        new.id = [int(farm["id"])]
        new.hectare = [float(farm["hectare"])]
        new.result_fm = [float(farm["result_fm"])]
        new.is_created_by = [device]
        new.has_city = [db.onto.City(city_name)]
        new.has_state_associated = [db.onto.State(state_name)]
        new.has_size = [db.onto.Size(size_to_name_onto(farm["size"]["name"]))]
        
        new.has_biome_associated = []
        for biome in farm["city"]["biomes"]:
          new.has_biome_associated.append(db.onto.Biome(clear_string(biome['name'])))
        
        new.has_attribute = []
        for key in farm["attributes"]:
          if key!="farm_id":
            if (farm["attributes"][key]):
              new.has_attribute.append(db.onto.Attribute(key))
            else:
              new.has_missing_attribute.append(db.onto.Attribute(key))
        
        new.has_production = []
        for production in farm["productions"]:
          name_prod = f'farm-{farm["id"]}_{clear_string(production["activity"])}_{production["id"]}'
          new_prod = db.onto.Production(name_prod)
          new_prod.num_area=[float(production["num_area"])]
          new_prod.has_activity=[db.onto.ProductionActivity(clear_string(production["activity"]))]
          new_prod.has_handling=[db.onto.ProductionHandling(clear_string(production["handling"]))]
          new_prod.has_state_associated=[db.onto.State(state_name)]

          if 'cultivation' in production:
            new_prod.is_agricultura = [True]
            new_prod.num_animals = [0]
            new_prod.has_cultivation = [db.onto.ProductionCultivation(clear_string(production["cultivation"]))]
          else:
            new_prod.num_animals = [int(production["num_animals"])]
            new_prod.is_agricultura = [False]
          
          new.has_production.append(new_prod)

      return jsonify({"Farm inserted": farm}), 200

    except OwlReadyError as e:
      print(f'Something went wrong in inserting: {e}')
      return jsonify({"Error": "Something went wrong in inserting"}), 400
    
    finally:
      db.save()
      db.close()
      

  def show(id):
    farm = onto.search_one(is_a=Farm, id=id)
    if farm == None: return jsonify({ 'error': 'Not found'}), 404
    json = farm.to_json()
    return jsonify(json)