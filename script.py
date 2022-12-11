from xml.dom import minidom
import mysql.connector
from mysql.connector import errorcode
import matplotlib.pyplot as plt
import re

# ====================== functions ===========================

# get the value of a node (given node)
def getNodeText(node):
    nodelist = node.childNodes
    result = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            result.append(node.data)
    return ''.join(result)



## ======================= main ==============================

# DEFINE MYSQL OBJECTS - connection, cursor, queries
try:
    conn = mysql.connector.connect(user='admin', password='Password', host='*', database='recalls') # endpoint removed for security
    cursor = conn.cursor()
except mysql.connector.Error as err:
    print(err)

add_records = ("INSERT INTO recalls (manu, comp, type) VALUES (%(manu)s, %(comp)s, %(type)s)")
get_most_commonly_recalled_manu = "SELECT manu, COUNT(*) AS magnitude FROM recalls GROUP BY manu ORDER BY magnitude DESC LIMIT 10" # get the manufacturer who is most commonly recalled from
get_most_commonly_recalled_comp = "SELECT comp, COUNT(*) AS magnitude FROM recalls GROUP BY comp ORDER BY magnitude DESC LIMIT 10" # get the component which is most commonly recalled

""" 
- The code below was used to parse 'rows.xml' and get every 'row' tag.    1 row = 1 recall
- Because my goal is to find the Top 10 Most Recalled Manufacturers & Components, I get the NodeText of each relevent element. 
- I use a dictionary to hold each element and its value. Each dictionary will be a record in the mySQL database.
- The code remains commented out because the database is currently populated. It takes a long time to add 26,000 entries to a DB.

# parse XML and collect all 'row' tags
doc = minidom.parse("rows.xml")
xml_rows = doc.getElementsByTagName("row") # returns a NodeList

# INSERT XML DATA INTO MYSQL
rows_to_mysql = []
row_count = 0

for i in xml_rows:
    row_count += 1
    m = str(getNodeText(i.getElementsByTagName("manufacturer")[0]))
    c = str(getNodeText(i.getElementsByTagName("component")[0]))
    r = str(getNodeText(i.getElementsByTagName("recall_type")[0]))
    row = {'manu':m, 'comp':c, 'type':r}
    rows_to_mysql.append(row)

    try:
        cursor.execute(add_records, row)
        cnx.commit()
        print(row_count, ' added - ', row)
    except mysql.connector.Error as err:
        print(err)
 """

# DEFINE LISTS
manu_names = []
manu_counts = []
comp_names = []
comp_counts = []
counter = 0

# READ MYSQL DATA AND PLOT
cursor.execute(get_most_commonly_recalled_manu)
print("== Top 10 Most Recalled Manufacturers ==")
for manu in cursor:
    counter += 1
    formatted_number = int(re.search(r'\d+', str(manu)).group())
    formatted_name = str(manu).rsplit(',', 1)[0].replace("'", "")[1:]
    manu_counts.append(formatted_number)
    manu_names.append(formatted_name)
    print(str(counter) + '. ' + formatted_name + " - " + str(formatted_number)) # format string  

counter = 0
cursor.execute(get_most_commonly_recalled_comp)
print("\n== Top 10 Most Recalled Components ==")
for comp in cursor:
    counter += 1
    formatted_number = int(re.search(r'\d+', str(comp)).group())
    formatted_name = str(comp).rsplit(',', 1)[0].replace("'", "")[1:].title()
    comp_counts.append(formatted_number)
    comp_names.append(formatted_name)
    print(str(counter) + '. ' + formatted_name + " - " + str(formatted_number)) # format string


# close mysql connection
cursor.close()
conn.close()

# ========= PLOTTING DATA WITH MATPLOTLIB ============

# manufacturer pie chart
labels = manu_names
sizes = manu_counts
explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0)  # only "explode" the largest (first) slice
fig1, ax1 = plt.subplots()
ax1.set_title('Top 10 Most Recalled Manufacturers\n')
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
caption = '"General Motors accounts for 21.5 percent of the Top 10"'
plt.figtext(0.5, 0.01, caption, wrap=True, horizontalalignment='center', fontsize=12)

# component pie chart
labels = comp_names
sizes = comp_counts
explode = (0.1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
fig2, ax2 = plt.subplots()
ax2.set_title('Top 10 Most Recalled Components\n')
ax2.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
caption = '"Equipment accounts for 21.9 percent of the Top 10"'
plt.figtext(0.5, 0.01, caption, wrap=True, horizontalalignment='center', fontsize=12)

plt.show()

#2916 unique manu names
#41 unique comp names
