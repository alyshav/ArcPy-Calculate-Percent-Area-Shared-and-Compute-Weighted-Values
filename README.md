# Calculate Percent Area Shared and Compute Weighted Values

**Purpose: use Arcpy & numpy to compute percent area shared between each feature contained in 2 input shapefiles**

+ Calculates Percent of Area Shared between features in 2 input shapefiles and Compute Weighted Attribute Values
+ p1_generate_ada_to_fsa_matrix: Used to calculate the percent of area each ADA occupies within each FSA. Example: an ADA with FID 1 comprises 55% of FSA with FID 15. We add 0.55 to the relationship matrix at m[FSA_FID][ADA_FID] to use in adding weighted attribute values we want to compute later.
+ p2_add_weighted_data.py: Used to add weighted attribute values based on relationship matrix values previously computed