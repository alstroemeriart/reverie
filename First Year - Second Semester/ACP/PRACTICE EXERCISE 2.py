"""
IT Helpdesk Ticket Priority & SLA Assigner

Assigns ticket priority and SLA target based on impact and urgency levels.

Inputs:
- Employee Name
- Department
- Issue Category (network/hardware/software)
- Impact Level (1-3)
- Urgency Level (1-3)

Outputs:
Displays ticket summary including priority, SLA target, and category note.
"""

employeeName = input("Enter employee name: ")
department = input("Enter department: ")
category = input("Enter issue category (network/hardware/software): ").lower() # Get category input and convert to lowercase for input consistency

impact = int(input("Enter impact level (1-3): ")) # Get impact level input and convert to integer
urgency = int(input("Enter urgency level (1-3): ")) # Get urgency level input and convert to integer

if impact == 3: # Determine priority based on impact and urgency levels
    if urgency == 3: # For impact level 3 and urgency level 3, assign highest priority
        priority = "P1 (Critical)"
    elif urgency >= 2: # For impact level 3 and urgency level 2, assign high priority
        priority = "P2 (High)"
    else: # For impact level 3 and urgency level 1, assign medium priority
        priority = "P3 (Medium)"
elif impact >= 2: # For impact level 2, determine priority based on urgency levels
    if urgency >= 2: # For impact level 2 and urgency level 2 or higher, assign high priority
        priority = "P2 (High)"
    else: # For impact level 2 and urgency level 1, assign medium priority
        priority = "P3 (Medium)"
else: # For impact level 1, assign lowest priority regardless of urgency
    priority = "P4 (Low)" 

if priority == "P1 (Critical)": # Set SLA target based on priority level
    sla = 4
elif priority == "P2 (High)":
    sla = 8
elif priority == "P3 (Medium)":
    sla = 24
else:
    sla = 72

if category == "network": # Set category note based on issue category
    note = "Check connectivity and ISP status."
elif category == "hardware":
    note = "Check device condition and peripherals."
else:
    note = "Check application errors and updates."

print("\nEmployee:", employeeName) # Display the ticket summary with all relevant information
print("Department:", department)
print("Category:", category)
print("Impact:", impact)
print("Urgency:", urgency)
print("Priority:", priority)
print("SLA Target:", sla, "hours") # Display SLA target in hours
print("Note:", note)
