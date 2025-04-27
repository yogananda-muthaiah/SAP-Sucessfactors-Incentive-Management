import subprocess
import pandas as pd
import sys

def manage_Modeling_Object(Modeling_Object):
    # Step 1: Login to Datasphere using host and secrets file
    dsp_host = '<URL of Datasphere>'
    secrets_file = '<path>/Login.json'
    command = f'datasphere login --host {dsp_host} --secrets-file {secrets_file}'
    subprocess.run(command, shell=True)  # Execute the login command
    
    # Step 2: Retrieve a list of all spaces in JSON format
    command = ['datasphere', 'spaces', 'list', '--json']
    result_spaces = subprocess.run(command, capture_output=True, shell=True, text=True)  # Run the command and capture output
    
    # Step 3: Parse the list of spaces from the command's output
    spaces = result_spaces.stdout.splitlines()  # Split output into individual lines
    
    ModelingObject_data = []  # Initialize a list to store Modeling Object data
    
    # Step 4: Check if the Modeling Object is 'spaces'
    if Modeling_Object == 'spaces':
        for space in spaces:
            if space == "[" or space == "]":
                continue  # Skip brackets in the JSON output
            space_id = space.strip()  # Extract space ID
            
            # Add space details to the data list
            ModelingObject_data.append({
                'Space ID': space_id.replace('"', '').replace(',', ''),
                'Technical Name': space_id.replace('"', '').replace(',', ''),
                'TYPE': Modeling_Object[:-1].upper()  # Set the TYPE as uppercase version of the input Modeling Object name
            })
    
    # Step 5: Process Modeling Objects for each space
    else:
        for space in spaces:
            if space == "[" or space == "]":
                continue  # Skip brackets in the JSON output
            space_id = space.strip()  # Extract space ID
            
            # Step 6: Retrieve Modeling Objects for the current space
            command = ['datasphere', 'objects', Modeling_Object, 'list', '--space', space_id.replace('"', '').replace(',', '')]
            result_ModelingObject = subprocess.run(command, capture_output=True, shell=True, text=True)  # Run the command
            
            # Step 7: Parse the Modeling Object data from the output
            ModelingObject_info = result_ModelingObject.stdout.splitlines()  # Split output into individual lines
            print("Checking "+Modeling_Object.upper()+" for space : "+space_id.replace('"', '').replace(',', ''))  # Log the space being checked
            
            # Step 8: Process each Modeling Object
            if len(ModelingObject_info) > 1:
                for flow in ModelingObject_info:
                    if '{' in flow or '}' in flow or '[' in flow or ']' in flow:
                        continue  # Skip brackets or braces in the output
                    cleaned_flow = flow.replace('"technicalName":', '').replace('"', '').strip()  # Clean up the output
                    
                    # Step 9: Add Modeling Object details to the data list
                    ModelingObject_data.append({
                        'Space ID': space_id.replace('"', '').replace(',', ''),
                        'Technical Name': cleaned_flow,
                        'TYPE': Modeling_Object[:-1].upper()  # Set the TYPE as uppercase version of the input Modeling Object name
                    })
    
    # Step 10: Write the collected data into a CSV file
    if ModelingObject_data:
        df = pd.DataFrame(ModelingObject_data)  # Create a DataFrame from the data list
        df.to_csv(Modeling_Object.upper()+'.csv', index=False)  # Save the DataFrame to a CSV file without the index
        print("Space vise all "+Modeling_Object.upper()+" have been written to "+Modeling_Object.upper()+".csv.")  # Log success message
    else:
        print("No Modeling Objects found.")  # Log message if no data was collected
    
    print('------------------------------------------------------------------------------------------------------------------------------------')  # Separator for readability
        
if __name__ == "__main__":
    # Check if an argument is provided via the command line
    if len(sys.argv) > 1:
        # Pass the first argument to the method
        manage_Modeling_Object(sys.argv[1])
    else:
        print("Please provide a Modeling Object name as an argument.")  # Log error message if no argument is provided
        
# Execute for predefined Modeling Objects
manage_Modeling_Object('remote-tables')
manage_Modeling_Object('local-tables')
manage_Modeling_Object('views')
manage_Modeling_Object('intelligent-lookups')
manage_Modeling_Object('data-flows')
manage_Modeling_Object('replication-flows')
manage_Modeling_Object('transformation-flows')
manage_Modeling_Object('task-chains')
manage_Modeling_Object('analytic-models')
manage_Modeling_Object('data-access-controls')
