import re

with open("bot.py", "r") as f:
    code = f.read()

# Fix 1 & Fix 2

# 1. Update parse_iso
old_parse_iso = '''def parse_iso(iso_str: str) -> datetime:
    if not iso_str: return datetime.min.replace(tzinfo=timezone.utc)
    s = iso_str.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(s)
    except:
        return datetime.min.replace(tzinfo=timezone.utc)'''

new_parse_iso = '''def parse_iso(iso_str: str) -> datetime:
    if not iso_str: return datetime.min.replace(tzinfo=timezone.utc)
    s = iso_str.replace('Z', '+00:00')
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except:
        return datetime.min.replace(tzinfo=timezone.utc)'''
code = code.replace(old_parse_iso, new_parse_iso)

# 2. Update get_owner_name and get_category_voice
old_owner = '''def get_owner_name(merchant: dict) -> str:
    ident = merchant.get("identity", {})
    return ident.get("owner_first_name") or ident.get("name") or "Partner"'''

new_owner = '''def get_owner_name(merchant: dict) -> str:
    ident = merchant.get("identity", {})
    return ident.get("owner_first_name") or ident.get("first_name") or ident.get("name") or "Partner"

def clean_prefix(name: str, prefix: str) -> str:
    if name.lower().startswith(prefix.lower()):
        return name[len(prefix):].strip()
    return name'''
code = code.replace(old_owner, new_owner)

old_voice = '''def get_category_voice(category: dict, cat_slug: str, owner: str) -> str:
    voice = category.get("voice", {})
    salutations = voice.get("salutation_examples", [])
    if salutations:
        return salutations[0].replace("{first_name}", owner).replace("{owner}", owner)
    
    if cat_slug == "dentists": return f"Dr. {owner}"
    elif cat_slug == "restaurants": return f"Chef {owner}"
    return f"Hi {owner}"'''

new_voice = '''def get_category_voice(category: dict, cat_slug: str, merchant: dict) -> str:
    voice = category.get("voice", {})
    salutations = voice.get("salutation_examples", [])
    owner = get_owner_name(merchant)
    m_name = get_merchant_name(merchant)
    
    if salutations:
        sal = salutations[0]
        if "Dr." in sal and owner.lower().startswith("dr."):
            owner = clean_prefix(owner, "dr.")
        if "Chef" in sal and owner.lower().startswith("chef"):
            owner = clean_prefix(owner, "chef")
            
        sal = sal.replace("{first_name}", owner)
        sal = sal.replace("{owner}", owner)
        sal = sal.replace("{chef_or_owner_first_name}", owner)
        sal = sal.replace("{pharmacist_name}", owner)
        
        sal = sal.replace("{gym_name}", m_name)
        sal = sal.replace("{salon_name}", m_name)
        sal = sal.replace("{restaurant_name}", m_name)
        sal = sal.replace("{pharmacy_name}", m_name)
        return sal
    
    if cat_slug == "dentists":
        return f"Dr. {clean_prefix(owner, 'dr.')}"
    elif cat_slug == "restaurants":
        return f"Chef {clean_prefix(owner, 'chef')}"
    return f"Hi {owner}"'''
code = code.replace(old_voice, new_voice)

# 3. Update compose_opportunity to call get_category_voice correctly
old_compose_call = '''    owner = get_owner_name(merchant)
    m_name = get_merchant_name(merchant)
    c_name = get_customer_name(customer)
    
    greeting = get_category_voice(category, cat_slug, owner)'''
    
new_compose_call = '''    owner = get_owner_name(merchant)
    m_name = get_merchant_name(merchant)
    c_name = get_customer_name(customer)
    
    greeting = get_category_voice(category, cat_slug, merchant)'''
code = code.replace(old_compose_call, new_compose_call)

with open("bot.py", "w") as f:
    f.write(code)

