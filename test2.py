table_structure = {
    'Company': ['Nintendo', 'Sony', 'Microsoft'],
    'Brand': ['Nintendo 3DS (3DS)', 'Nintendo DS (DS)', 'Nintendo Switch (NS)', 'Wii (Wii)', 'Wii U (WiiU)',
              'PlayStation 3 (PS3)', 'PlayStation 4 (PS4)', 'PlayStation Vita (PSV)',
              'Xbox 360 (X360)', 'Xbox One (XOne)'],
    'Location': ['Europe', 'Japan', 'North America', 'Other'],
    'Season': ['DEC', 'JUN', 'MAR', 'SEP'],
    'Year': ['2013','2014','2015','2016','2017','2018','2019','2020']
}

def convert_filter_condition_to_string(condition):
    attribute_names = list(table_structure.keys())
    explanations = []
    for i, value in enumerate(condition):
        if value in table_structure[attribute_names[i]]:
            explanations.append(f"{attribute_names[i]} = {value}")
        else:
            for key, values in table_structure.items():
                if value in values:
                    explanations.append(f"{key} = {value}")
                    break
    return ', '.join(explanations)

# Example filter condition
filter_condition = ('Sony', 'PlayStation 4 (PS4)', 'Other', '2013')

# Convert filter condition to human-readable explanation
explanation = convert_filter_condition_to_string(filter_condition)

# Print the explanation
print(explanation)
