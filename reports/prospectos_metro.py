"""Prospect list for San Juan, Guaynabo and Bayamón (October 2026).

Each entry was found on Instagram/Facebook or a booking directory and then searched by name;
"web" says what that search showed. Followers are not listed because Instagram could not be
opened from the research environment. Run this file to regenerate prospectos-metro-2026-10.csv.
"""

import csv
from pathlib import Path

IG = "https://www.instagram.com/{}/"
FB = "https://www.facebook.com/{}"

# pago: Alto = professional practice, several staff/locations, high prices or premium area.
P = [
 # cat, nombre, pueblo, direccion, instagram, facebook, telefono, whatsapp, email, resenas, senales, pago, web, confianza, fuentes
 ("Barbería","167 Barber Shop","Bayamón","Ave. Ramón Luis Rivera, 00957",IG.format("167barbershop"),FB.format("OscarBarberShopPR"),"787-515-2122","","colonoscar22@gmail.com","Listado en Fresha","Abre los 7 días; hasta 10 PM de jueves a sábado","Medio","Sin web propia: solo Instagram, Facebook y Fresha","Alta",["https://www.fresha.com/lvp/167barbersshop-ramon-luis-rivera-avenue-bayamon-3o9GPN"]),
 ("Barbería","Santurce La Barbería Salón","San Juan","Ave. De Diego, Santurce",IG.format("santurcelabarberiasalon"),"","787-312-4474","787-312-4474","","Reservas por Booksy","Concepto premium tipo spa (afeitado con toalla, vino al cliente); salió en Metro PR","Alto","Sin web propia: Instagram y Booksy","Alta",["https://www.metro.pr/estilo-vida/2016/11/22/regreso-barberia-tradicional"]),
 ("Barbería","Estudio La Barbería (Cecilio Men's Stylist)","Guaynabo","Carr. 833 / Ave. 177 #1499, Local 3, Los Frailes",IG.format("estudiolabarberia"),"","787-382-3097","","","Reservas por Booksy","Corte desde $30 y corte con barba desde $40: clientela que paga","Alto","Sin web propia: Instagram y Booksy","Alta",[]),
 ("Barbería","JJ Barbershop Old San Juan","San Juan","300 Calle San Francisco, Viejo San Juan",IG.format("jjbarbershopoldsanjuan"),"","787-318-4323","","","No encontradas","Zona turística; abre martes a sábado","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Barbería","Sport BarberShop","San Juan","173 Calle Los Andes, 00926",IG.format("sportbarbershop_"),"","","","","No encontradas","Se presenta como 'The Best Shop in Guaynabo'","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Uñas","Retoque Guaynabo","Guaynabo","Los Jardines Shopping Center, Calle Marginal 130, Frailes",IG.format("retoque_guaynabo"),"","939-409-9090","","","4.9 en Fresha","Precios publicados ($25–$35 por servicio) en centro comercial","Medio","Sin web propia: Instagram y Fresha","Alta",[]),
 ("Uñas","Pintauñas Nails & Salon","Guaynabo","56-62 Av. Esmeralda, 00969",IG.format("pintaunasnailsalon"),"","787-466-8529","","","Listado en Fresha","Ofrece fish pedicure (poco común); abre lunes a sábado","Medio","Sin web propia: Instagram y directorios","Alta",[]),
 ("Uñas","Jireh Nail Salón","Guaynabo","PR-838, Guaynabo Rental Park, 00969",IG.format("jirehnail"),"","939-325-6714","","","Reservas por Booksy","Uñas y cejas con hilo","Medio","Sin web propia: Instagram, Booksy y Fresha","Alta",[]),
 ("Uñas","Crea'tif Salon and Spa","Guaynabo","Ave. Esmeralda",IG.format("creatifsalon"),"","787-789-6412","","","No encontradas","Cabello, uñas, spa y cejas: varios servicios y personal","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Uñas","Mónaco Nails","San Juan / Guaynabo (verificar)","Por confirmar",IG.format("monaconailspr"),"","","","","No encontradas","Por evaluar en su Instagram","Medio","No apareció web al buscar por nombre","Baja",[]),
 ("Salón","Curl Boss Salon","San Juan","Ave. 65 de Infantería",IG.format("curlbosspr"),"","787-640-8800","787-640-8800","","Salió en Remezcla","Nicho de cabello rizado; dueños con podcast propio","Alto","Sin web propia: Instagram y WhatsApp","Alta",["https://remezcla.com/lists/beauty/7-local-beauty-wellness-businesses-bad-bunny-residency/"]),
 ("Salón","Top Beauty Salón","San Juan","1367 Ave. Roosevelt",IG.format("topbeautysalonpr"),"","787-781-9642","787-781-9642 / 787-508-0298","","No encontradas","Dos líneas de WhatsApp activas","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Salón","bloOm Salon & Spa","Guaynabo","100 Av. San Patricio, 00968",IG.format("bloomsalonspapr"),"","787-781-2525","","","Listado en Fresha","Zona San Patricio (alto poder adquisitivo); salón + spa","Alto","Sin web propia: Instagram y Fresha","Alta",[]),
 ("Salón","Jean C Stilo","Bayamón","Bayamón (también Kissimmee, FL)",IG.format("jeancstilo"),"","787-998-2614","","","No encontradas","Dos ubicaciones (PR y Florida); color, uñas y maquillaje","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Salón","Top Nail Bar","Bayamón","Plaza Bayamón Mall",IG.format("topnailbar"),"","787-334-0101","787-678-3355","","No encontradas","Local dentro de un mall (renta alta); cabello, uñas y belleza","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Food truck","La Chulada Foodtruck","Guaynabo","Carr. Alejandrino Km 1.3, Sector Melia",IG.format("la_chulada_foodtruck"),"","787-664-5551","787-664-5551","","4.9 con más de 1,000 calificaciones en Uber Eats","Mucho volumen de ventas","Alto","Sin web propia: Instagram, Uber Eats y Platea PR","Alta",["https://www.plateapr.com/en/directory/metro/guaynabo/restaurantes/la-chulada-foodtruck-guaynabo"]),
 ("Food truck","La Disputa","San Juan","San Juan",IG.format("la_disputa_food_truck"),"","787-223-1433","","","No encontradas","Sándwiches, empanadas y smash burgers; abre lunes a sábado","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Food truck","Sabores Gourmet Criollo","Bayamón","Restaurante en Bayamón; truck en Levittown",IG.format("saboresgourmetcriollo21"),"","787-998-6982","939-900-1193 (truck)","","No encontradas","Dos puntos de venta: restaurante y food truck","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Food truck","Bayamón Food Truck Station (parque)","Bayamón","Ave. Lomas Verdes",IG.format("bayamonfoodtruckstation"),"","","","","No encontradas","Parque de food trucks: el operador cobra a varios trucks","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Food truck","GFT Park – Guaynabo Food Truck Park","Guaynabo","Guaynabo",IG.format("guaynabofoodtruckpark"),"","","","","No encontradas","Más de 14 food trucks en un solo parque","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Restaurante / repostería","Ladelos Pastelillos","Bayamón","Bayamón y Cataño",IG.format("ladelospastelillos"),"","787-639-4054","","","No encontradas","Dos locales; más de 40 sabores","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Restaurante / repostería","Guaynabo Bakery & Pizzeria","Guaynabo","Av. Paz Granela 1476",IG.format("guaynabobakery"),"","939-338-3226","","","En Uber Eats","Abre los 7 días desde las 5 AM","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Restaurante / repostería","Mejor Aquí PR","Bayamón","Bayamón",IG.format("mejoraqui.pr"),"","787-619-6453","","","No encontradas","Comida criolla, mariscos y mojitos","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Restaurante / repostería","Golden Hour","Bayamón","Bayamón",IG.format("restaurante_golden_hour"),"","","","","No encontradas","Comida china y japonesa","Medio","No apareció web al buscar por nombre","Baja",[]),
 ("Restaurante / repostería","El Rincón del Repostero","Bayamón","Bayamón",IG.format("elrincondelrepostero_"),"","787-400-7146","","","No encontradas","Repostería con local; abre lunes a sábado","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Restaurante / repostería","Michi's Cakes","San Juan","San Juan",IG.format("michiscakespr"),"","787-447-7772","","","No encontradas","Bizcochos, cupcakes y galletas por encargo","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Taller","Eurotechniques – Taller de Mecánica","Bayamón","#66 Esteban Padilla","",FB.format("eurotechniquespr"),"787-269-3111","","","No encontradas","Más de 35 años; especialistas en carros europeos","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Taller","Auto Precision","Bayamón","Ave. Lomas Verdes F-8","",FB.format("AutoPrecision"),"787-786-6810","","","Perfil de Google Business","Taller establecido en Lomas Verdes","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Taller","MK Auto Service PR","Bayamón","377 Calle Comerío","","https://www.facebook.com/p/MK-Auto-Service-PR-100085318856976/","787-702-9229","","","No encontradas","Escanea Chrysler, Dodge, Jeep y Ram hasta 2024","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Taller","Import Service","Guaynabo","Guaynabo","",FB.format("importservicepr"),"","","","No encontradas","Más de 17 años con BMW, Mercedes y Mini (clientes de carros de lujo)","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Taller","CJ AutoTech","San Juan","Ave. Gobernador Piñero","",FB.format("ServiJ"),"787-297-5554","","","No encontradas","Mecánica y electromecánica","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Dentista","Clínica Dental Bayamón – Dr. Eduardo Crespo","Bayamón","Medical Ophthalmic Plaza, 1875 Carr. 2, Ste. 203",IG.format("crespodmd"),"","939-310-2555","","","No encontradas","Dos dentistas; implantes e Invisalign; acepta CareCredit","Alto","Sin web propia: solo directorios médicos e Instagram","Alta",["https://local.newpatientsinc.com/dental/dr-eduardo-crespo-bayamon-pr"]),
 ("Dentista","IA Dental – Dra. Ingrid Irizarry","Guaynabo","Guaynabo",IG.format("iadental45"),"","787-720-2125","","","No encontradas","Odontología general; dos teléfonos de oficina","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Dentista","Dra. Carla Rodríguez Bonilla (dentista pediátrica)","Bayamón","Bayamón",IG.format("dra.carlarodriguez"),"","787-900-3545","","","No encontradas","Especialista en pediatría","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Dentista","Local Dental","San Juan","San Juan",IG.format("localdental"),"","787-281-8106","","","No encontradas","General, pediatría y periodoncia; dos teléfonos","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Dentista","Dra. Alexandra Rodríguez (dentista pediátrica)","San Juan","San Juan",IG.format("dentistapediatricaalexandra"),"","787-508-1412","","","No encontradas","Especialista en pediatría","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Quiropráctico","Aviva Family Chiropractic – Dr. Ariel Tomey","San Juan","15 Av. Luis Muñoz Rivera, #2010","",FB.format("AvivaFamilyChiropractic"),"787-417-7794","","","No encontradas","Acepta planes; masajes y estiramientos; solo tiene página de citas en JaneApp","Alto","Sin web propia: Facebook y JaneApp","Alta",["https://avivachiropractic.janeapp.com"]),
 ("Quiropráctico","Grupo Quiropráctico de Guaynabo","Guaynabo","B-3 Calle Marginal, Urb. Villa Lissette","",FB.format("grupoquiropracticodeguaynabo"),"787-999-6570","","","No encontradas","Tres quiroprácticos; pediatría, prenatal y deportes","Alto","Sin web propia: Facebook y directorios","Alta",["https://practicefinder.newpatientsinc.com/chiro/dr-lee-cardona-dc-guaynabo-pr/"]),
 ("Quiropráctico","Galería Quiropráctica","Guaynabo y Bayamón","2102 Calle Turquesa, Guaynabo",IG.format("galeriaquiropractica"),FB.format("galeriaquiro"),"787-708-7766","","","No encontradas","24 años; dos oficinas (Guaynabo 787-708-7766 y Bayamón 787-963-1737)","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Quiropráctico","V Chiropractic Center","Guaynabo","100 Ave. San Patricio, Suite 203","","https://www.facebook.com/p/V-Chiropractic-Center-100094324312506/","787-990-5070","","","No encontradas","Oficina en San Patricio","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Médico","Centro de Medicina Interna – Dr. Juan Bayron","San Juan","San Juan","",FB.format("cmibay"),"787-783-0399","","centrodemedicinainterna@gmail.com","No encontradas","Usa Gmail, señal de que no tiene dominio ni web","Alto","Sin web propia: usa email de Gmail y Facebook","Alta",[]),
 ("Médico","Clínica de Medicina Interna – Dra. Marielle Sánchez","Bayamón","Bayamón","",FB.format("dramariellesanchez"),"","","","No encontradas","Práctica privada de medicina interna","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Médico","Salus","Guaynabo","Ave. Casa Linda #1, Suite 101","",FB.format("saluspr"),"787-789-1996","","","No encontradas","Oficina médica en Guaynabo","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Médico","Médica Integral","San Juan (Río Piedras)","San Juan","",FB.format("Medicaintegralsjr"),"","","","No encontradas","Medicina integral","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Médico","Clínica Pediátrica 020","Por confirmar",
  "Por confirmar",IG.format("pediatrica020"),"","","","","No encontradas","Pediatría, neonatología, dental y adolescentes en un solo lugar","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Abogado","Lcdo. Edgar Villanueva Rivera, Abogado-Notario","Bayamón","Calle 15 T-34, Urb. Flamboyán Gardens",IG.format("lcdo.villanuevarivera"),FB.format("VillanuevaRiveralawpr"),"787-310-4416","","","No encontradas","Civil, criminal, herencias y notaría","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Abogado","Aboga Bufete Jurídico","Por confirmar","Por confirmar","","https://www.facebook.com/p/Aboga-Bufete-Jur%C3%ADdico-100063584443496/","787-945-5193","","","No encontradas","Familia, daños, laboral, herencias y contratos","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Abogado","Lcda. Chrisired Morales Negrón","Por confirmar","Por confirmar",IG.format("suabogadanotario"),"","","","","No encontradas","Abogada-notario activa en Instagram","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Abogado","Nieves & Morales Abogados-Notarios","Por confirmar","Por confirmar",IG.format("nievesmoraleslawoffices"),"","","","","No encontradas","Bufete con dos socios","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Abogado","Tu Notario PR","San Juan","San Juan","",FB.format("tunotariopr"),"","","","No encontradas","Servicios notariales","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Contador","Premier CPA & Business Consulting Group","Bayamón","Bayamón","",FB.format("premiercpapr"),"787-428-0202","","","No encontradas","Contabilidad, nómina, planillas y consultoría","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Contador","CPA JLFA","Bayamón","Bayamón","",FB.format("CPAJLFA"),"787-995-3836","","","No encontradas","Auditoría, contabilidad, nómina y contribuciones","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Contador","CPA Juan García Padró","Guaynabo","Guaynabo","",FB.format("cpagarciapadropr"),"","","","No encontradas","Contabilidad y nómina","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Contador","Vega Taxes Services","Guaynabo","Guaynabo","",FB.format("taxesservices"),"787-518-3058","","","No encontradas","Preparación de planillas","Medio","No apareció web al buscar por nombre","Media",[]),
 ("Contador","CPA Johmary Meléndez","Por confirmar","Por confirmar",IG.format("planillaspr_cpa"),"","","","","No encontradas","Tiene podcast propio ('Vino el Viernes'): invierte en mercadeo","Alto","No apareció web al buscar por nombre","Media",["https://www.audible.co.uk/podcast/Vino-el-Viernes/B0CCN54TCX"]),
 ("Techos / solar","Insignia Roofing – Sellado de Techos","Guaynabo","Guaynabo","","https://www.facebook.com/p/Insignia-Roofing-Sellado-de-Techos-100076794886278/","787-366-2446","","","No encontradas","Certificados por DACO y Danosa; garantía de 10 años","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Techos / solar","MF Home Solutions Inc.","San Juan","San Juan","",FB.format("mfhomesolutions"),"","","","No encontradas","Sellado con sistema Danosa; garantía de 10 años","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Techos / solar","Sellado de Techos con Danosa","Bayamón","Bayamón","",FB.format("selladodanosa"),"787-526-5709","","","No encontradas","Filtraciones garantizadas","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Techos / solar","Marin Membrana","Bayamón","Bayamón","",FB.format("marinmembrana"),"787-316-7898","","","No encontradas","Venta e instalación de membrana","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Techos / solar","Sellado de Techos Uretano","Bayamón","Bayamón","",FB.format("TechosPR"),"787-226-3650","","","No encontradas","Sellado y venta de selladores industriales","Alto","No apareció web al buscar por nombre","Media",[]),
 ("Alquiler vacacional","Isla del Encanto Vacation Rentals","San Juan (Condado) y Río Grande","Condado",
  "",FB.format("haciendaelyunque"),"939-342-6640","","","No encontradas","Casas de lujo en Condado y Río Grande","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Alquiler vacacional","Isla Verde Vacation Rentals","Carolina (Isla Verde)","Isla Verde","",FB.format("IslaVerdeVacationRentals"),"(703) 327-6225","","hmsdc@aol.com","No encontradas","Dueño fuera de PR; email de AOL (sin dominio propio)","Alto","Sin web propia: usa AOL y Facebook","Media",[]),
 ("Alquiler vacacional","PR Vacation Apartment","San Juan (Condado)","Condado","",FB.format("prvacationapartment"),"","","","No encontradas","Penthouses de 3 cuartos en Condado","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Alquiler vacacional","San Juan Short Term Rental","San Juan","Condado y Ocean Park","",FB.format("SanJuanShortTermRental"),"","","","No encontradas","Varias propiedades en Condado y Ocean Park","Alto","No apareció web al buscar por nombre","Baja",[]),
 ("Alquiler vacacional","San Juan Vacation Rentals","San Juan","San Juan","",FB.format("SanJuanVacation"),"787-410-6003","","","No encontradas","Varias propiedades","Alto","No apareció web al buscar por nombre","Baja",[]),
]

DESCARTADOS = [
 ("Natural Health Chiropractic","Santurce","Ya tiene web: naturalhealthpr.com"),
 ("Health Chiropractic and More","Bayamón y otros","Ya tiene web: tucolumnahabla.com"),
 ("El Verde Dental","Caguas","Tiene web en Wix y está fuera del área"),
 ("Solar Now Puerto Rico","San Juan","Empresa grande con financiamiento propio; casi seguro tiene web"),
 ("DMP Legal & Notary Services","San Juan","Usa email con dominio propio (dmplawpr.com)"),
 ("Huachinango","Guaynabo","Restaurante con salones de eventos; parece tener web"),
 ("JL Barber Studio / Barbero Ema","Bayamón","Buenas reseñas en Booksy (5.0), pero no les encontré Instagram ni Facebook"),
]

# Corrections found while checking booking platforms (Oct 2026).
UPDATES = {
 "Crea'tif Salon and Spa": {"direccion": "Centro Comercial, Edificio B, Ave. Lopategui Local 3", "telefono": "787-668-9645",
                            "resenas": "Clientas de años la recomiendan en Fresha"},
 "Sport BarberShop": {"direccion": "273 Calle Los Andes, 00926", "telefono": "787-216-7618"},
 "Top Nail Bar": {"resenas": "4.9 con 2,590 votos en Fresha"},
 "Jean C Stilo": {"direccion": "3V7 Ave. Lomas Verdes, Bayamón, 00956", "resenas": "5.0 (32) en Booksy"},
 "Santurce La Barbería Salón": {"direccion": "312 Ave. De Diego, Santurce", "resenas": "5.0 en Booksy: 807 + 190 + 89 + 36 reseñas entre 4 perfiles"},
 "Curl Boss Salon": {"resenas": "Reseñas en Vagaro; salió en Remezcla"},
}

# Booking platform each business uses today, and what it costs them (published 2026 prices).
# Booksy: $29.99/mes + $20 por empleado; Boost cobra 30% de la 1.a visita del cliente nuevo ($10–$100).
# Fresha: $19.95/mes individual o $14.95 por empleado; 20% (mín. $6) por cliente nuevo del marketplace.
# Vagaro: $23.99/mes + $10 por usuario. Setmore: gratis hasta 4 empleados. Jane: desde $54/mes.
# Uber Eats: 7–10% en pickup y 20–30% en delivery.
PLATAFORMA = {
 "Santurce La Barbería Salón": ("Booksy (4 perfiles de barbero)", "https://booksy.com/en-us/1236100_santurce-la-barberia-salon_barber-shop_7_usa", "$90–$120+ al mes (4 perfiles) + 30% de la 1.a visita de clientes de Boost"),
 "Estudio La Barbería (Cecilio Men's Stylist)": ("Booksy", "", "$30–$70 al mes según cuántos barberos + comisiones de Boost"),
 "Jireh Nail Salón": ("Booksy", "", "Desde $29.99 al mes + comisiones de Boost"),
 "Jean C Stilo": ("Booksy (2 perfiles en PR y 1 en Florida)", "https://booksy.com/en-us/1521265_jean-c-stilo-salon_hair-salon_34799_san-juan", "$60–$90 al mes entre sus perfiles"),
 "167 Barber Shop": ("Fresha", "https://www.fresha.com/lvp/167barbersshop-ramon-luis-rivera-avenue-bayamon-3o9GPN", "$19.95–$45 al mes + 20% por cliente nuevo del marketplace"),
 "Retoque Guaynabo": ("Fresha", "", "$19.95–$45 al mes + 20% por cliente nuevo del marketplace"),
 "JJ Barbershop Old San Juan": ("Fresha y Setmore", "https://www.fresha.com/lvp/jj-barber-shop-old-san-juan-calle-de-san-francisco-san-juan-Eko3Gb", "$19.95+ al mes en Fresha (Setmore puede ser gratis)"),
 "Sport BarberShop": ("Fresha", "https://www.fresha.com/lvp/sport-barbershop-calle-los-andes-san-juan-xXxYj6", "$19.95–$45 al mes + 20% por cliente nuevo del marketplace"),
 "Crea'tif Salon and Spa": ("Fresha", "https://www.fresha.com/lvp/creatif-salon-and-spa-avenue-lopategui-guaynabo-7x9b25", "$30–$75 al mes (varias empleadas) + 20% por cliente nuevo"),
 "Top Nail Bar": ("Fresha (88 servicios)", "https://www.fresha.com/a/top-nail-bar-bayamon-plaza-bayamon-qed67sbu", "$75–$150 al mes (equipo grande) + 20% por cliente nuevo del marketplace"),
 "Pintauñas Nails & Salon": ("Aparece en Fresha (confirmar)", "", "Por confirmar"),
 "bloOm Salon & Spa": ("Aparece en Fresha (confirmar)", "", "Por confirmar"),
 "Curl Boss Salon": ("Vagaro (y aparece en Fresha)", "https://www.vagaro.com/curlboss", "$34–$60 al mes en Vagaro según usuarios"),
 "Aviva Family Chiropractic – Dr. Ariel Tomey": ("Jane App", "https://avivachiropractic.janeapp.com", "Desde $54 al mes"),
 "La Chulada Foodtruck": ("Uber Eats", "https://www.ubereats.com/us-es/store/la-chulada-foodtruck/OtW4PpDAXfCDMDdeslloBw", "7–10% de cada pedido para recoger y 20–30% de cada delivery"),
 "Guaynabo Bakery & Pizzeria": ("Uber Eats", "", "7–10% de cada pedido para recoger y 20–30% de cada delivery"),
}

# Bengal Media PR packages. Setup is one payment; the monthly fee covers hosting, domain, SSL,
# small changes and support. PR market reference: $450–$2,295 one-time; boutique maintenance $50–$200/mo.
PAQUETES = {
 "presencia":   ("Presencia", 650, 49, "Página bilingüe con su marca, fotos, servicios, WhatsApp, mapa y SEO local."),
 "conectada":   ("Citas conectadas", 900, 69, "Presencia + un botón 'Reservar' en cada servicio que abre ese servicio en su Booksy, Fresha o Vagaro. Esas citas entran como directas, sin la comisión de cliente nuevo del marketplace."),
 "propias":     ("Citas propias", 1600, 99, "Presencia + reservas dentro de la página: cada servicio con su precio, duración y barbero o técnica, confirmación por WhatsApp o email y recordatorios. Reemplaza Booksy o Fresha."),
 "pedidos":     ("Pedidos directos", 1200, 79, "Presencia + menú con pedidos para recoger por WhatsApp o pago en línea, sin comisión de Uber Eats en los clientes que ya le conocen."),
 "profesional": ("Profesional", 1500, 99, "Varias secciones (servicios, equipo, planes, preguntas), formulario de contacto, SEO local y Google Business Profile."),
 "profesional_citas": ("Profesional + citas", 2000, 129, "Profesional + citas en línea por servicio dentro de la página."),
 "alquiler":    ("Reservas directas", 1800, 99, "Página de la propiedad con galería, calendario de disponibilidad sincronizado con Airbnb y solicitud de reserva directa (sin la comisión de la plataforma)."),
}

def paquete_para(nombre: str, categoria: str) -> str:
    plat = PLATAFORMA.get(nombre, ("",))[0]
    if categoria in ("Food truck", "Restaurante / repostería"):
        return "pedidos"
    if categoria == "Alquiler vacacional":
        return "alquiler"
    if categoria in ("Dentista", "Médico", "Quiropráctico"):
        return "profesional_citas"
    if categoria in ("Abogado", "Contador", "Techos / solar", "Taller"):
        return "profesional"
    if plat.startswith(("Booksy", "Fresha", "Vagaro")):
        return "propias" if nombre in ("Santurce La Barbería Salón", "Top Nail Bar", "Jean C Stilo", "Crea'tif Salon and Spa") else "conectada"
    return "presencia"

FIELDS = ["categoria","nombre","pueblo","direccion","instagram","facebook","telefono","whatsapp","email",
          "resenas","senales_de_pago","potencial_pago","verificacion_web","confianza","fuentes"]

def ola(d: dict) -> str:
    """Wave 1: no website, reachable on WhatsApp and/or Instagram, location and phone confirmed."""
    if (d["instagram"] or d["whatsapp"]) and d["confianza"] != "Baja":
        return "1"
    return ""


def prioridad(d: dict) -> int:
    """Lower is first: can pay, certainly has no website, WhatsApp confirmed, already pays a platform."""
    return ((d["potencial_pago"] != "Alto") * 4 + (d["confianza"] != "Alta") * 2 + (not d["whatsapp"])
            - (d["plataforma_citas"] not in ("No detectada", "") and not d["plataforma_citas"].startswith("Aparece")))


EXTRA = ["ola", "prioridad", "plataforma_citas", "link_plataforma", "costo_actual_plataforma", "paquete", "setup_usd", "mensual_usd"]

def rows():
    for p in P:
        d = dict(zip(FIELDS, p))
        d["fuentes"] = " ".join(p[-1])
        d.update(UPDATES.get(d["nombre"], {}))
        plat, link, costo = PLATAFORMA.get(d["nombre"], ("No detectada", "", ""))
        key = paquete_para(d["nombre"], d["categoria"])
        nombre_paq, setup, mensual, _ = PAQUETES[key]
        d.update(plataforma_citas=plat, link_plataforma=link, costo_actual_plataforma=costo,
                 paquete=nombre_paq, setup_usd=setup, mensual_usd=mensual, paquete_key=key)
        d["ola"] = ola(d)
        d["prioridad"] = prioridad(d) if d["ola"] else ""
        yield d

INDUSTRIA = {
 "Barbería": "barberia", "Uñas": "unas", "Salón": "salon", "Food truck": "foodtruck",
 "Restaurante / repostería": "restaurante", "Taller": "taller", "Dentista": "dentista",
 "Quiropráctico": "quiropractico", "Médico": "medico", "Abogado": "abogado", "Contador": "contador",
 "Techos / solar": "solar", "Alquiler vacacional": "alquiler",
}
# Industry exceptions where the business is clearly another kind.
INDUSTRIA_NOMBRE = {"Top Nail Bar": "unas", "Crea'tif Salon and Spa": "salon"}


def crear_clientes(ola_n: str = "1") -> list[str]:
    """Create sites/clients/<slug>.json for every business in the wave that has none yet.

    Only verified facts go in. "preview" stays false and "estado" says what's missing, so no
    generic page is built until /brandkit and /mockup add their logo, photos and real content.
    """
    import json, re, sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from sites.build import ROOT, slugify

    existing = {json.loads(f.read_text(encoding="utf-8")).get("name"): f.stem for f in (ROOT / "clients").glob("*.json")}
    created = []
    for d in rows():
        if d["ola"] != ola_n or d["nombre"] in existing:
            continue
        name = re.sub(r"\s*[–(].*$", "", d["nombre"]).rstrip(",")
        slug = slugify(name)
        path = ROOT / "clients" / f"{slug}.json"
        if path.exists():  # never overwrite a client file, even if its name differs from the report
            continue
        digits = re.sub(r"\D", "", d["whatsapp"].split("/")[0].split("(")[0])
        client = {
            "preview": False,
            "estado": "Esperando logo y fotos de su Instagram (sites/clients/%s/raw/)" % slug,
            "slug": slug,
            "industry": INDUSTRIA_NOMBRE.get(d["nombre"], INDUSTRIA[d["categoria"]]),
            "name": name,
            "municipio": d["pueblo"].split(" (")[0],
            "address": d["direccion"] if d["direccion"] != "Por confirmar" else "",
            "phone": d["telefono"],
            "email": d["email"],
            "social": {k: v for k, v in (("instagram", d["instagram"]), ("facebook", d["facebook"])) if v},
            "lead": {
                "nombre_reporte": d["nombre"], "ola": ola_n, "prioridad": d["prioridad"], "channel": "WhatsApp" if digits else "Llamada / Instagram DM",
                "email": d["email"], "why": d["senales_de_pago"], "resenas": d["resenas"],
                "plataforma": d["plataforma_citas"], "costo_plataforma": d["costo_actual_plataforma"],
                "paquete": d["paquete"], "precio": f"${d['setup_usd']:,} + ${d['mensual_usd']}/mes",
                "sources": d["fuentes"].split(),
            },
        }
        if digits:
            client["whatsapp"] = ("1" + digits) if len(digits) == 10 else digits
        path.write_text(json.dumps(client, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created.append(slug)
    return created


if __name__ == "__main__" and "--clientes" in __import__("sys").argv:
    for slug in crear_clientes():
        print("creado sites/clients/%s.json" % slug)
    raise SystemExit

if __name__ == "__main__":
    out = Path(__file__).with_name("prospectos-metro-2026-10.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS + EXTRA, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows())
    print(f"{len(P)} prospectos -> {out}")
