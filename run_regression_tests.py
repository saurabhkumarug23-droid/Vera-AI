import sys
import bot
from datetime import datetime, timezone

errors = []

print("Running Regression Tests...")

# 1. Identity Tests
bot.contexts.clear()
cat_dentists = {"slug": "dentists", "voice": {"salutation_examples": ["Dr. {first_name}"]}}
merchant_dentist = {"identity": {"first_name": "Dr. Meera"}}
if bot.get_category_voice(cat_dentists, "dentists", merchant_dentist) != "Dr. Meera":
    errors.append("Dentist duplicate prefix failed")

cat_gyms = {"slug": "gyms", "voice": {"salutation_examples": ["{gym_name} team"]}}
merchant_gym = {"identity": {"name": "Karan Gym"}}
if bot.get_category_voice(cat_gyms, "gyms", merchant_gym) != "Karan Gym team":
    errors.append("Gym placeholder failed")

cat_pharm = {"slug": "pharmacies", "voice": {"salutation_examples": ["Hi {pharmacist_name}"]}}
merchant_pharm = {"identity": {"name": "Vikas Pharmacy", "owner_first_name": "Vikas"}}
if bot.get_category_voice(cat_pharm, "pharmacies", merchant_pharm) != "Hi Vikas":
    errors.append("Pharmacy placeholder failed")
    
cat_rest = {"slug": "restaurants", "voice": {"salutation_examples": ["Hi {chef_or_owner_first_name}"]}}
merchant_rest = {"identity": {"name": "Suresh Rest", "owner_first_name": "Suresh"}}
if bot.get_category_voice(cat_rest, "restaurants", merchant_rest) != "Hi Suresh":
    errors.append("Restaurant placeholder failed")
    
cat_salon = {"slug": "salons", "voice": {"salutation_examples": ["Hi {salon_name}"]}}
merchant_salon = {"identity": {"name": "Glamour Salon"}}
if bot.get_category_voice(cat_salon, "salons", merchant_salon) != "Hi Glamour Salon":
    errors.append("Salon placeholder failed")

# 2. Date parsing (Timezone safe)
dt = bot.parse_iso("2026-10-31")
if dt.tzinfo is None:
    errors.append("Date parsing produced naive datetime")
    
try:
    now = bot.parse_iso("2026-04-20T10:00:00Z")
    diff = dt - now
    if diff.days <= 0:
        errors.append("Date math failed")
except Exception as e:
    errors.append(f"Date math threw exception: {e}")

# 3. Unresolved template safety
# Let's test a message with {first_name} left behind.
t = bot.unresolved_template_variables("Hi {first_name}, how are you?")
if not t:
    errors.append("Unresolved template check failed to catch '{first_name}'")

# Let's ensure the fallback works.
res = bot.compose_opportunity({"identity": {"name": "{not_a_placeholder"}}, {}, {"_meta": {"kind": "dormant_with_vera"}, "payload": {"payload": {"days_since_last_merchant_message": 10}}}, None, now)
# It should abort if it has {
if res is not None:
    errors.append("compose_opportunity did not return None on unresolved placeholder")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)
print("All regression tests PASS")
