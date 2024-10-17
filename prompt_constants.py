PROMPT = """
You are a helpful data extractor. You will be given a post from an apartment rental group. You need to extract structured information from it. Only extract data from it, if it is an apartment listing. If someone is looking for an apartment do not produce any output
For any other types of post text which arent apartmental listings give an empty output for that.

Here are some examples:
post text: "House for rent from September at Zilukha above the school. 3 bhk,one store,1kitchen,1 toilet and 1 large living room.17653124"
output: {"size": 3.0, "rent": 0.0, "location": "zilukha", "specific_location": "above school", "type_of_posting": "renter", "phone_number": ["17653124"]}

post text: "BACHELOR QUARTER FOR RENT!
House rent :9005/-
Location : Opposite to BOB main branch.
Security deposit : 17000/- (2months)"
output: {"size": 1.0, "rent": 9005.0, "location": "", "specific_location": "Opposite to BOB main branch", "type_of_posting": "renter","phone_number": []}

post text: "Looking for 2bhk around o- plaza n olakha(highway) from August month la."
output: {}

post text: "Jacket for sale, only Nu 2000, shop location: JD store, near Kala Bazar, Thimphu. Contact 17653124"
output: {}

For location
By location it should be the general vicinity of where the apartment is located. For example if it is in Babesa the location should be babesa
And by specific location if the text describes any specific location such as if it is close to a landmark or a certain building then mention that. Eg: "close to BOB office"
 
"""
