import markdown, os
from flask import jsonify, request
from app import app
from src.controllers.FarmController import *

@app.route('/farms', methods=['POST']) 
def farm_store():
  farm = request.json
  return FarmController.store(farm)