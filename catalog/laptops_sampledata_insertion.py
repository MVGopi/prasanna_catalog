from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from Laptops_Database_Setup import *

db_engine = create_engine('sqlite:///laptops_catalog.db')


Base.metadata.bind = db_engine


Database_Session = sessionmaker(bind=db_engine)


session=Database_Session()


session.query(User).delete()


session.query(Company).delete()

session.query(Laptop).delete()


#user = User(name="venkata gopi", email="venkatagopi894@gmail.com",picture="https://drive.google.com/drive/folders/0B-DCot06UZdQcHZ4ajVic1hRQjQ")

#insert some of laptop companies
mac = Company(name="Apple Macbook", user_id=1, icon="https://images-na.ssl-images-amazon.com/images/I/218MZ3obWgL.jpg")

dell = Company(name="Dell Inspiron", user_id=2, icon="https://softlay.net/wp-content/uploads/2016/01/Dell-Icon-200x200.jpg")

hp = Company(name="Hewlett Packard", user_id=3, icon="https://vignette.wikia.nocookie.net/logopedia-fanon/images/5/54/Hewlett-Packard-Logo-2015.png/ revision/latest?cb=20160311201459")

session.add(mac)

session.add(dell)

session.add(hp)

session.commit()


#insert some laptops to the particular companies

Apple1 = Laptop(name="Apple MacBook Pro", price="1,32,990INR", ram="8GB",
                      rom="256GB", image="https://5.imimg.com/data5/NF/WC/MY-32657793/best-good-condition-apple-markbook-laptops-and-other-brands-500x500.jpg", company_id=1)

Apple2 = Laptop(name="Apple MacBook Pro", price="1,32,990INR", ram="8GB",
                      rom="256GB", image="https://5.imimg.com/data5/NF/WC/MY-32657793/best-good-condition-apple-markbook-laptops-and-other-brands-500x500.jpg", company_id=1)

Apple3 = Laptop(name="Apple MacBook Pro", price="1,32,990INR", ram="8GB",
                      rom="256GB", image="https://5.imimg.com/data5/NF/WC/MY-32657793/best-good-condition-apple-markbook-laptops-and-other-brands-500x500.jpg", company_id=1)


session.add(Apple1)

session.add(Apple2)

session.add(Apple3)

session.commit()

print("Data inserted successfully")

                                                     


