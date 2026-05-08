
"""
Inicializace databáze a vytvoření ukázkových dat.
Spusťte: python init_db.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, User, Category, Station
import uuid


def init_db():
    with app.app_context():
        db.create_all()
        print("✓ Tabulky vytvořeny.")

        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@skola.cz', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Admin účet vytvořen (admin / admin123)")


        if not User.query.filter_by(username='ucitel').first():
            teacher = User(username='ucitel', email='ucitel@skola.cz', role='teacher')
            teacher.set_password('ucitel123')
            db.session.add(teacher)
            print("✓ Učitelský účet vytvořen (ucitel / ucitel123)")


        categories_data = [
            ('💻', 'Informatika a IT', '#3B82F6', 'Programování, sítě, kybernetická bezpečnost'),
            ('⚙️', 'Technické obory', '#F59E0B', 'Strojírenství, elektrotechnika, mechatronika'),
            ('🎨', 'Umění a design', '#EC4899', 'Výtvarná výchova, grafický design, architektura'),
            ('🔬', 'Přírodní vědy', '#10B981', 'Fyzika, chemie, biologie, ekologie'),
            ('📚', 'Humanitní obory', '#8B5CF6', 'Jazyky, literatura, dějepis, filozofie'),
            ('🏋️', 'Tělesná výchova', '#EF4444', 'Sport, zdravý životní styl, atletika'),
            ('🎵', 'Hudba a umění', '#F97316', 'Hudební výchova, sborový zpěv, orchestr'),
            ('📐', 'Matematika', '#06B6D4', 'Algebra, geometrie, statistika'),
        ]

        cats = {}
        for icon, name, color, desc in categories_data:
            if not Category.query.filter_by(name=name).first():
                cat = Category(name=name, icon=icon, color=color, description=desc)
                db.session.add(cat)
                db.session.flush()
                cats[name] = cat
                print(f"  + Kategorie: {name}")
            else:
                cats[name] = Category.query.filter_by(name=name).first()


        stations_data = [
            {
                'name': 'Počítačová učebna A',
                'room_number': 'A201',
                'floor': 2,
                'description': 'Moderně vybavená učebna s 30 počítači pro výuku programování a práci s grafickými programy. Studenti se zde učí programovat v Pythonu, Javascriptu i C++.',
                'equipment': '30× PC (Intel Core i7, 16GB RAM), 2× velká obrazovka, projektor, interaktivní tabule, síťové prvky Cisco',
                'projects': 'Robotický fotbal, webové aplikace pro místní firmy, databázový projekt pro správu školní knihovny',
                'contact_person': 'Ing. Pavel Novák',
                'contact_email': 'novak@skola.cz',
                'order': 1,
                'categories': ['Informatika a IT', 'Matematika'],
            },
            {
                'name': 'Laboratoř chemie',
                'room_number': 'B105',
                'floor': 1,
                'description': 'Plně vybavená chemická laboratoř se bezpečnostním vybavením. Studenti provádějí pokusy od základní analýzy látek po organickou syntézu.',
                'equipment': 'Digestoře, soupravy pro titraci, spektrofotometr, pH metry, centrifuga, mikrovlnná trouba pro syntézu',
                'projects': 'Analýza pitné vody z místního vodovodu, výroba přírodních barviv, projekt čistá energie',
                'contact_person': 'RNDr. Jana Procházková',
                'contact_email': 'prochazkova@skola.cz',
                'order': 2,
                'categories': ['Přírodní vědy'],
            },
            {
                'name': 'Dílna strojírenství',
                'room_number': 'D001',
                'floor': 0,
                'description': 'Kompletně vybavená strojní dílna v suterénu školy. Studenti pracují s CNC stroji, soustruhy a 3D tiskárnami pod dohledem odborných mistrů.',
                'equipment': '2× CNC fréza, 3× soustruh, 4× 3D tiskárna (FDM i SLA), svářečky MIG/TIG, kompresor, ruční nářadí',
                'projects': 'Výroba součástí pro školní roboty, tisk prototypů pro místní startupy, renovace historických exponátů',
                'contact_person': 'Mistr Tomáš Horák',
                'contact_email': 'horak@skola.cz',
                'order': 3,
                'categories': ['Technické obory'],
            },
            {
                'name': 'Multimediální studio',
                'room_number': 'A302',
                'floor': 3,
                'description': 'Profesionální nahrávací studio a fotografická ateliér. Studenti tvoří podcasty, natáčejí videa a fotografují pro školní magazín.',
                'equipment': 'Nahrávací konzola, mikrofony Rode, DSLR kamery Canon, greenscreen, osvětlovací soupravy, střihové stanice s Adobe Premiere',
                'projects': 'Školní YouTube kanál, roční fotografická výstava, podcast "Škola mluví"',
                'contact_person': 'MgA. Lucie Benešová',
                'contact_email': 'benesova@skola.cz',
                'order': 4,
                'categories': ['Umění a design', 'Informatika a IT'],
            },
            {
                'name': 'Jazyková učebna',
                'room_number': 'C203',
                'floor': 2,
                'description': 'Moderní jazyková učebna vybavená jazykovou laboratoří. Vyučují se zde angličtina, němčina, francouzština a španělština.',
                'equipment': 'Jazyková laboratoř (30 sluchátek), interaktivní tabule, konferenční systém, knižní fond',
                'projects': 'Dálkové lekce s partnerskými školami v Německu a UK, překladatelský kroužek, divadelní představení v cizím jazyce',
                'contact_person': 'Mgr. Eva Kratochvílová',
                'contact_email': 'kratochvilova@skola.cz',
                'order': 5,
                'categories': ['Humanitní obory'],
            },
            {
                'name': 'Tělocvična a fitness',
                'room_number': 'E001',
                'floor': 0,
                'description': 'Velká tělocvična pro míčové sporty a přilehlé fitness centrum. Pořádají se zde i meziškolní turnaje.',
                'equipment': 'Basketbalové koše, volejbalová síť, badmintonové kurty, fitness stroje, protahovací plochy',
                'projects': 'Meziškolní liga ve florbalu, sportovní den, kurzy sebeobrany',
                'contact_person': 'Mgr. Martin Šimánek',
                'contact_email': 'simanek@skola.cz',
                'order': 6,
                'categories': ['Tělesná výchova'],
            },
            {
                'name': 'Elektrotechnická laboratoř',
                'room_number': 'D102',
                'floor': 1,
                'description': 'Laboratoř pro praktickou výuku elektrotechniky a elektroniky. Studenti sestavují obvody, programují mikrokontroléry a pracují s Arduino.',
                'equipment': 'Osciloskopy, multimetry, napájecí zdroje, Arduino, Raspberry Pi, pájiecí stanice, součástky',
                'projects': 'Chytrý skleník (IoT projekt), domácí meteorologická stanice, automatické zavlažování',
                'contact_person': 'Ing. Radek Blažek',
                'contact_email': 'blazek@skola.cz',
                'order': 7,
                'categories': ['Technické obory', 'Informatika a IT'],
            },
            {
                'name': 'Výtvarný ateliér',
                'room_number': 'C301',
                'floor': 3,
                'description': 'Prostorný výtvarný ateliér s přirozeným světlem. Studenti tvoří malby, sochy, keramiku a grafický design.',
                'equipment': 'Keramická pec, hrnčířský kruh, grafický tisk, plátna, malířské stojany, grafické tablety Wacom',
                'projects': 'Výroční výstava prací studentů, ilustrace školního almanachu, street art projekt',
                'contact_person': 'Mgr. art. Petra Dvořáčková',
                'contact_email': 'dvorackova@skola.cz',
                'order': 8,
                'categories': ['Umění a design'],
            },
        ]

        for s_data in stations_data:
            if not Station.query.filter_by(room_number=s_data['room_number']).first():
                cat_names = s_data.pop('categories')
                s_data['qr_code'] = str(uuid.uuid4()).replace('-', '')[:12]
                station = Station(**s_data)
                station.categories = [cats[n] for n in cat_names if n in cats]
                db.session.add(station)
                print(f"  + Stanoviště: {station.name} ({station.room_number})")

        db.session.commit()
        print("\n✅ Databáze úspěšně inicializována!")
        print("\nPřihlašovací údaje:")
        print("  Administrátor: admin / admin123")
        print("  Učitel:        ucitel / ucitel123")
        print("\nSpusťte aplikaci: python app.py")
        print("Administrace:      http://localhost:5000/admin")


if __name__ == '__main__':
    init_db()
