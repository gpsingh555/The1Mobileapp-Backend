

class UserSetting:

    def user_profile(self, user):
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "mobile": user.username,
            "dob": user.user_profile.dob,
            "user_bio": user.user_profile.user_bio,
            "image": user.user_profile.image.url,
            "country": {
                "country_id": user.user_profile.country.id,
                "country_name": user.user_profile.country.name
            }
        }

    def get_user_profile(self, user, data):
        pass