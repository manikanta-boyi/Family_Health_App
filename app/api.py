from flask import Blueprint,jsonify,request
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required,get_jwt_identity
from .models import User,FamilyMember,HealthRecord
from werkzeug.security import check_password_hash


api = Blueprint('api',__name__,url_prefix='/api/')


@api.route('/login',methods=['POST'])
def api_login():
    """
    API endpoint for user login.
    Expects JSON input with 'email' and 'password'.
    Returns access and refresh JWTs on success, or JSON error message on failure.
    """
    email = request.json.get('email',None)
    password = request.json.get('password',None)

    if not email or not password:
        return jsonify({"msg": "Missing email or password in request"}), 400
    
    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password,password):
        access_token = create_access_token(identity=str(user.id),fresh=True)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify(access_token=access_token,refresh_token=refresh_token),200
    else:

        return jsonify({"msg": "Invalid email or password"}), 401


@api.route('/members',methods=['GET'])
@jwt_required()
def api_list_members():
    current_user_id = get_jwt_identity()
    

    members = FamilyMember.query.filter_by(user_id = int(current_user_id)).all()
    

    members_data = []
    for member in members:
        member_dict = member.to_dict()
        members_data.append(member_dict)
        print(f"  DEBUG: Member ID {member.id} dict:")
        for key, value in member_dict.items():
            print(f"    Key: {key}, Value: {value}, Type: {type(value)}")

    
    return jsonify(members_data),200

@api.route('/member/<int:member_id>/record',methods = ['GET'])
@jwt_required()
def api_view_record(member_id):
    current_user_id= get_jwt_identity()
    member = FamilyMember.query.get(member_id)
    if not member:
        return jsonify({'msg':"member not found"}),404
    if int(current_user_id) != member.user_id:
        return jsonify({'msg':'unauthorized request'}),403
    records = HealthRecord.query.filter_by(family_member_id=member.id).all()

    records_data = [record.to_dict() for record in records]

    return jsonify(records_data), 200



    
