# This file defines the expected schema structure for MongoDB collections.
# No explicit schema is enforced by MongoDB, but we keep it for documentation.

# users collection:
# {
#   "user_id": int,
#   "username": str,
#   "first_name": str,
#   "is_verified": bool,
#   "is_premium": bool,
#   "premium_expiry": datetime,
#   "referral_code": str,
#   "referred_by": int,
#   "created_at": datetime
# }

# groups collection:
# {
#   "group_id": int,
#   "title": str,
#   "welcome_message": str,
#   "log_channel": int,
#   "settings": dict
# }

# invite_links collection:
# {
#   "link_id": str,
#   "invite_link": str,
#   "group_id": int,
#   "creator_id": int,
#   "max_uses": int,
#   "current_uses": int,
#   "expiry_date": datetime,
#   "created_at": datetime,
#   "is_revoked": bool
# }

# link_usage collection:
# {
#   "user_id": int,
#   "link_id": str,
#   "group_id": int,
#   "joined_at": datetime
# }

# admins collection:
# {
#   "user_id": int,
#   "role": str,  # "owner", "super_admin", "admin"
#   "added_by": int,
#   "added_at": datetime
# }

# premium_users collection:
# {
#   "user_id": int,
#   "expiry_date": datetime,
#   "plan_type": str
# }

# referrals collection:
# {
#   "referrer_id": int,
#   "referred_id": int,
#   "reward_given": bool,
#   "created_at": datetime
# }

# settings collection:
# {
#   "key": str,
#   "value": str,
#   "updated_at": datetime
# }

# backups collection:
# {
#   "filename": str,
#   "created_by": int,
#   "created_at": datetime
# }
