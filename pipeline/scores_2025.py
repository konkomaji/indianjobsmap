#!/usr/bin/env python3
"""
AI exposure and India-context scores for all NCO-2015 3-digit occupation groups
present in PLFS CY2025 microdata.

Scored on the Karpathy-style anchored 0-10 scale adapted for India (see
4_score.py for the full anchor text). Each entry carries:
  ai_exposure, ai_rationale, automation_risk, formalization_potential,
  gig_potential, growth_outlook, india_note

These were authored by a labour-economist reasoning pass over each occupation
in the Indian context, then merged with PLFS 2025 employment statistics by
5b_compile_2025.py. Where 4_score.py is run with an ANTHROPIC_API_KEY, those
LLM scores can replace these; this file is the offline fallback so the
visualisation is always complete.
"""

# Better names for codes PLFS left unlabelled
NAME_FIX = {
    "133": "ICT Service Managers",
    "224": "Paramedical Practitioners",
    "312": "Production & Operations Supervisors",
    "324": "Veterinary Technicians & Assistants",
}

# code: (ai, automation, formal, gig, growth, ai_rationale, india_note)
S = {
# ── 1 Managers ──────────────────────────────────────────────
"111": (5,1,9,0,"stable","Policy drafting and file-noting are increasingly AI-assisted, but authority, discretion and field administration stay human.","The coveted sarkari naukri. IAS, IPS, IFS and state-service officers. Lakhs sit UPSC and state PSC exams every year for a few thousand posts."),
"112": (6,2,7,1,"growing","Strategy, financial analysis and reporting are AI-augmentable, but leadership, deal-making and accountability remain personal.","CEOs and MDs of registered companies. Many are promoter-owners of MSMEs; high informality here means family-run firms counted as self-employed."),
"121": (6,2,8,2,"growing","Business and admin managers lean on dashboards and reports that AI now drafts, but people management and judgement stay human.","Backbone of India's organised sector and GCC boom. Bengaluru, Hyderabad and Pune global capability centres employ lakhs of mid-managers."),
"122": (6,3,6,3,"growing","Campaign copy, audience analysis and CRM work are squarely in AI's path, freeing managers for strategy.","Sales and PR managers across FMCG, retail and D2C brands. Digital marketing has pulled this role into the platform economy."),
"132": (5,4,6,2,"growing","Production planning and quality reports are AI-assisted, but factory-floor supervision is physical and relational.","Manufacturing and construction managers riding the PLI scheme and infra push. Demand strong in auto, electronics and cement."),
"133": (7,3,7,3,"fast-growing","ICT service managers oversee work that AI is reshaping fastest: code, cloud, support. Their teams' output is highly automatable.","India's IT services and GCC engine. TCS, Infosys, Wipro plus hundreds of global captives. AI is changing what these teams deliver."),
"134": (6,2,6,2,"growing","Managers of professional-service firms gain from AI drafting and research, but client trust and sign-off stay human.","Heads of CA firms, law practices, consultancies, hospitals. Mostly urban, organised, high-value services."),
"141": (4,3,6,4,"growing","Booking, billing and inventory are digitising via apps, but hospitality is a physical, guest-facing trade.","Hotel and restaurant managers. Tourism recovery and the cloud-kitchen and OYO model are reshaping the trade."),
"142": (5,4,7,4,"stable","Inventory, pricing and POS analytics are AI-ready, but store operations stay physical.","Retail and wholesale managers. Organised retail (Reliance, DMart, Vishal) is slowly formalising a kirana-dominated trade."),
"143": (6,3,6,3,"growing","Service-sector managers use AI for scheduling, reporting and customer analytics across varied operations.","Managers across logistics, facilities, events and other services. Broad, urban, organised-sector category."),
# ── 2 Professionals ─────────────────────────────────────────
"214": (7,3,6,3,"growing","Civil, mechanical and chemical engineering design and analysis are heavily AI-augmentable, though site work stays physical.","Engineers across infra, manufacturing and PSUs. India produces over 15 lakh engineering graduates a year; underemployment is real."),
"215": (8,3,6,3,"growing","Electrotechnology design, simulation and testing are deep in AI's path; much of the work is computational.","Electrical, electronics and telecom engineers. Demand rising with semiconductor, EV and 5G push."),
"216": (8,3,6,3,"growing","Architectural drawing, rendering and structural calc are being transformed by generative and parametric AI tools.","Architects and designers. Urban construction boom sustains demand; CAD and BIM already standard."),
"221": (5,2,7,2,"growing","Diagnosis support and documentation are AI-assisted, but examination, procedures and patient trust are deeply human.","Doctors. India has roughly 1 doctor per 1,500 people, badly skewed to cities. Rural posts stay vacant despite demand."),
"222": (4,2,8,2,"fast-growing","Records and monitoring digitise, but nursing is hands-on care AI cannot deliver.","Nurses and midwives. India is a top global exporter of nurses; domestic shortage persists, especially rural."),
"223": (3,2,6,2,"stable","AYUSH practice is consultative and physical; AI offers reference support at most.","Ayurveda, Yoga, Unani, Siddha and Homeopathy practitioners. AYUSH is government-backed and formalising under the AYUSH Ministry."),
"224": (5,2,7,2,"growing","Paramedical assessment and reporting gain AI support, but care delivery is physical.","Paramedical practitioners: physiotherapists, optometrists, lab and dialysis specialists. Fast-growing allied-health demand."),
"225": (4,2,6,2,"stable","Veterinary diagnosis is AI-assistable, but animal handling and field practice stay manual.","Veterinarians. Dairy is the world's largest; livestock and pet-care demand both rising."),
"226": (5,2,7,2,"growing","Health professionals' documentation and analysis are AI-augmentable; delivery stays human.","Dieticians, audiologists, public-health and other health professionals. Growing with insurance and wellness spend."),
"231": (7,3,6,2,"stable","Lecture prep, grading and research drafting are AI-augmentable, but teaching and mentorship stay human.","University and college teachers. NEP 2020 and the higher-ed expansion drive demand; contract teaching is widespread."),
"232": (6,3,8,3,"fast-growing","Vocational trainers can use AI for content, but skill demonstration is hands-on.","ITI and vocational instructors. Skill India, PMKVY and the apprenticeship push expand this role rapidly."),
"233": (6,3,6,3,"stable","Secondary teachers gain AI lesson and grading help, but classroom management is human.","Secondary-school teachers. RTE and state schooling sustain a huge workforce; private coaching parallels it."),
"234": (5,3,6,3,"stable","Primary teaching is relational and developmental; AI assists prep, not delivery.","Primary and pre-primary teachers, including Anganwadi-linked staff. Largest teaching segment, heavily female."),
"235": (6,4,5,5,"growing","Tutoring content and assessment are highly automatable; ed-tech already uses AI heavily.","Coaching-centre and ed-tech tutors. BYJU'S-era boom and bust; private tutoring is a vast informal market."),
"241": (8,3,6,3,"growing","Accounting, audit and financial analysis are squarely in AI's path; much is rule-based.","CAs, CFAs and finance professionals. GST and digital finance expand demand; AI reshapes routine work."),
"242": (7,3,6,2,"stable","HR, admin and compliance documentation are highly AI-augmentable.","HR and administration professionals across organised firms and government."),
"243": (7,4,6,4,"growing","Sales analytics, lead generation and outreach copy are deeply automatable.","Sales and marketing professionals. D2C, e-commerce and digital ads pull this into the platform economy."),
"251": (9,3,6,4,"fast-growing","Software development is among the most AI-exposed occupations: code generation, testing and debugging all advancing fast. Demand still grows as developers become more productive.","India's flagship knowledge job. About 54 lakh IT professionals; the sector earns over 250 billion dollars in exports. AI is the defining force here."),
"252": (8,4,6,3,"growing","Database and network administration is increasingly automated by AI ops and cloud tooling.","Database, network and systems professionals. Cloud migration and data-centre growth sustain demand."),
"261": (7,3,6,3,"stable","Legal research, drafting and review are highly AI-augmentable, but court craft and client trust stay human.","Lawyers and legal professionals. Huge informal bar; AI legal tools are arriving in Indian firms."),
"263": (5,2,5,2,"stable","Social and religious work is relational; AI offers research and admin support only.","Social workers, counsellors, clergy and religious workers. Large NGO and faith sector, much of it informal."),
"264": (8,3,5,4,"stable","Writing, translation and journalism are directly in generative AI's path; volume work is most exposed.","Authors, journalists and translators. Shrinking print, growing digital and regional-language content."),
"265": (6,3,4,4,"stable","AI generates images, music and video, exposing commercial creative work while live performance stays human.","Artists, musicians, actors and performers. Vast informal sector from films to wedding bands; OTT expands demand."),
# ── 3 Technicians & Associate Professionals ─────────────────
"311": (6,4,6,3,"growing","Engineering technicians' drafting, testing and monitoring are AI-augmentable; field work stays physical.","Civil, electrical and mechanical technicians. Infra and manufacturing growth sustain demand."),
"312": (5,4,6,2,"stable","Supervisors use AI dashboards for planning, but floor supervision is physical and relational.","Production and operations supervisors in mining, manufacturing and construction."),
"313": (6,5,6,2,"stable","Process-control monitoring is increasingly automated by sensors and AI, though plant work stays on-site.","Process-control technicians in power, chemical and refining plants. Organised, often PSU."),
"321": (5,4,7,3,"fast-growing","Diagnostic imaging and lab analysis are AI-assisted, but sample handling and patient contact stay physical.","Lab, radiology and pharma technicians. Diagnostics chains (Dr Lal, Metropolis) are formalising the trade fast."),
"322": (4,3,8,2,"fast-growing","Nursing associates' monitoring digitises, but bedside care is hands-on.","ANMs, GNM associates and nursing assistants. Backbone of rural and urban primary care; formalising under NHM."),
"324": (4,3,6,3,"stable","Veterinary assistance is hands-on animal work; AI gives reference support only.","Veterinary technicians and AI (artificial insemination) workers. Dairy and livestock sustain demand."),
"325": (5,3,7,3,"growing","Health associates' records and scheduling are AI-ready, but care is physical.","Pharmacy, dental and other health associates. Growing with retail pharmacy and clinic chains."),
"331": (8,4,7,3,"stable","Bookkeeping, tax filing and financial-record work are highly automatable; this is core AI territory.","Accounting clerks, tax preparers and insurance agents. GST and digital tax push reshape the work."),
"332": (6,4,6,5,"growing","Sales and purchasing agents' lead and order work is automatable; relationships keep some human edge.","Procurement and sales agents across trade. B2B platforms (Udaan, IndiaMART) are digitising the role."),
"333": (6,4,7,5,"growing","Business-service agents' matching and paperwork are automatable via platforms.","Real-estate, recruitment and travel agents. NoBroker, Naukri and MakeMyTrip platformise the trade."),
"334": (7,4,6,2,"declining","Secretarial and admin scheduling, minutes and correspondence are directly automatable.","Executive secretaries and admin assistants. A shrinking role as AI absorbs routine office work."),
"335": (5,3,8,1,"stable","Inspection reporting digitises, but regulatory field checks stay human.","Government regulatory and inspection associates: customs, tax, licensing. Formal, secure public jobs."),
"341": (6,3,6,3,"stable","Legal and social associates' documentation is AI-augmentable; field and client work stays human.","Paralegals, social-work associates and related staff."),
"342": (3,2,5,5,"fast-growing","Coaching and training are physical; AI offers analytics, not delivery.","Fitness trainers, sports coaches and yoga instructors. Urban wellness boom; cult.fit-style platforms expand gig work."),
"343": (5,3,5,5,"growing","Photography, design and culinary associate work is partly AI-exposed (editing, recipes) but craft stays manual.","Photographers, chefs-de-partie and artistic associates. Wedding and events economy is huge and informal."),
"351": (7,4,7,3,"growing","ICT operations and support are increasingly automated by AI ops and self-healing systems.","IT support and operations technicians. Backbone of the digital economy; AI reshapes L1/L2 support."),
"352": (6,5,6,3,"stable","Telecom installation monitoring automates, but tower and line work stays physical.","Telecom and broadcasting technicians. 5G rollout sustains field demand."),
# ── 4 Clerical Support ──────────────────────────────────────
"411": (8,4,6,2,"declining","General clerical work, filing, data handling and correspondence, is among the most automatable of all jobs.","General office clerks across government and private offices. Slowly shrinking as offices digitise."),
"412": (7,4,5,2,"declining","Secretarial scheduling and correspondence are squarely automatable.","Secretaries. A declining clerical role under digital and AI pressure."),
"413": (9,5,5,2,"declining","Keyboard and data-entry work is near-maximum AI exposure; AI already does most of it.","Data-entry and typing operators. A classic disappearing job as automation advances."),
"421": (7,5,7,3,"declining","Cashiering and teller work is automatable via UPI, ATMs and self-checkout.","Bank tellers, cashiers and collectors. UPI and digital banking are shrinking counter roles fast."),
"422": (7,5,6,4,"declining","Information-desk and call work is being absorbed by chatbots and voice AI.","Receptionists, enquiry and call-centre clerks. BPO voice work is highly AI-exposed."),
"431": (8,4,7,3,"declining","Numerical and accounting clerical work is rule-based and highly automatable.","Accounting and payroll clerks. GST automation and accounting software reduce demand."),
"432": (6,5,6,3,"stable","Stores, logistics and dispatch records digitise via WMS and AI, but warehouse work stays physical.","Stores, stock and transport clerks. E-commerce warehousing (Flipkart, Amazon) reshapes the role."),
"441": (7,4,6,2,"declining","Miscellaneous clerical work is broadly automatable.","Mailroom, coding and other clerks. Declining with office digitisation."),
# ── 5 Service & Sales ───────────────────────────────────────
"511": (4,3,6,5,"growing","Booking and information tasks digitise, but guiding and attending are in-person.","Flight attendants, travel guides and conductors. Tourism and aviation recovery drive demand."),
"512": (2,3,5,5,"growing","Cooking is manual and sensory; AI touches menus and ordering, not the wok.","Cooks across dhabas, restaurants and homes. Cloud kitchens and Swiggy/Zomato reshape the trade."),
"513": (3,4,5,6,"growing","Order-taking digitises via apps and kiosks, but serving is physical.","Waiters and bartenders. QSR and cafe boom; platform-based food service growing."),
"514": (2,3,7,7,"fast-growing","Beauty work is hands-on; AI offers booking and recommendation only.","Hairdressers and beauticians. Urban Company and salon chains are formalising a vast informal trade."),
"515": (3,3,6,5,"stable","Caretaking and housekeeping are physical service jobs AI cannot perform.","Building caretakers, housekeepers and supervisors. Facility-management firms are organising the sector."),
"516": (3,3,5,6,"growing","Personal services are in-person; platforms digitise booking, not delivery.","Other personal-service workers: pet groomers, valets, astrologers. Apps like Urban Company expand reach."),
"521": (3,4,5,5,"stable","Street vending is physical; UPI digitises payment, not the stall.","Street and market vendors. PM SVANidhi micro-loans and UPI are formalising parts of this huge informal trade."),
"522": (4,4,7,4,"stable","Shopkeeping is physical retail; POS, inventory AI and quick-commerce reshape it at the edges.","Kirana shopkeepers and shop sales staff. About 1.3 crore kiranas; quick-commerce (Blinkit, Zepto) pressures them."),
"523": (7,5,7,3,"declining","Cashier and ticketing work is automatable via self-service and digital payment.","Cashiers and ticket clerks. Cinemas, toll, transport; digital ticketing shrinks counters."),
"524": (5,4,6,5,"growing","Retail selling is partly automatable via e-commerce; in-store advice stays human.","Retail salespersons, telemarketers and demonstrators. Organised retail and e-commerce reshape the role."),
"531": (3,2,6,4,"growing","Childcare is relational and physical; AI offers scheduling at most.","Childcare workers, Anganwadi and creche staff, teacher aides. ICDS employs over 13 lakh Anganwadi workers."),
"532": (3,2,7,4,"fast-growing","Personal health care is hands-on; AI helps records, not bathing or feeding.","Home health aides and personal-care workers. Ageing population and home-care apps drive fast growth."),
"541": (3,4,7,3,"growing","Security monitoring is partly automatable via cameras and AI analytics, but guarding is physical presence.","Security guards, police and protective staff. Private security is one of India's largest employers, formalising under PSARA."),
# ── 6 Agriculture ───────────────────────────────────────────
"611": (1,2,5,2,"declining","Crop growing is physical, outdoor and weather-driven; AI advisory exists but does not do the work.","Market gardeners and crop farmers, India's single largest occupation. Small holdings, monsoon-dependent, deeply informal."),
"612": (2,2,5,2,"stable","Animal rearing is hands-on; AI offers herd and yield advisory only.","Dairy and livestock farmers. India is the world's largest milk producer; cooperatives like Amul anchor the sector."),
"613": (1,2,5,1,"declining","Mixed farming is physical subsistence work AI cannot perform.","Mixed crop-and-animal smallholders. Classic Indian marginal farmer, near-total informality."),
"621": (2,3,5,2,"stable","Forestry is outdoor physical work; AI assists mapping and monitoring.","Forestry and plantation workers. Tribal and forest-fringe livelihoods; MGNREGA supplements income."),
"622": (2,3,5,2,"declining","Fishing and hunting are physical; AI helps catch-mapping at most.","Marine and inland fishers. Coastal and riverine communities; mechanisation slow."),
"631": (1,1,4,1,"declining","Subsistence crop farming is pure physical survival work outside AI's reach.","Subsistence crop farmers. Among the poorest workers; landholdings fragmenting each generation."),
"632": (1,1,4,1,"declining","Subsistence livestock keeping is manual, low-income work.","Subsistence livestock farmers. Goats, poultry and cattle for survival; lowest measured incomes in PLFS."),
"633": (1,1,4,1,"declining","Subsistence mixed farming is physical survival work.","Subsistence mixed farmers. Marginal holdings combining crops and animals; deeply informal."),
"634": (1,2,4,1,"declining","Subsistence fishing is manual outdoor work.","Subsistence fishers. Small-craft inland and coastal fishing; among the lowest earners."),
# ── 7 Craft & Trades ────────────────────────────────────────
"711": (1,3,6,4,"growing","Masonry is skilled physical work; AI and prefab touch planning, not the trowel.","Masons and building-frame workers. Construction is India's second-largest employer; PMAY housing sustains demand."),
"712": (2,3,6,4,"growing","Finishing trades are manual; some prefabrication reduces site work.","Plasterers, tilers and building finishers. Urban construction boom drives steady demand."),
"713": (2,4,6,5,"stable","Painting and cleaning are physical; AI plays no real role.","Painters and building cleaners. Urban Company and asian-paints-linked services formalise parts of the trade."),
"721": (3,5,6,3,"stable","Sheet-metal and structural work is partly automatable by CNC and robotics in organised units.","Welders and structural-metal workers. Fabrication demand from infra and manufacturing."),
"722": (2,4,5,3,"declining","Blacksmithing is a traditional manual craft fading against industrial production.","Blacksmiths and toolmakers. A shrinking traditional trade, mostly rural and informal."),
"723": (3,4,6,6,"growing","Machinery repair is hands-on diagnostic work; AI assists fault-finding.","Auto, AC and machinery mechanics. EV transition reshapes auto repair; platforms like Pitstop add gig work."),
"731": (3,3,5,5,"stable","Handicraft is manual artistry; AI cannot replicate the hand, though it affects design and marketing.","Handicraft and precision workers: jewellery, handlooms, carving. GI-tagged crafts and export demand sustain them."),
"732": (6,6,6,3,"declining","Printing is heavily automated; digital media erodes the trade.","Printing-trades workers. Declining with the shift to digital media."),
"741": (3,5,6,5,"growing","Electrical equipment work is physical installation; AI assists diagnostics.","Electricians and electrical fitters. Construction, solar and EV charging drive demand; Urban Company gig work grows."),
"742": (4,5,6,5,"growing","Electronics and telecom installation is hands-on; AI assists fault-finding.","Electronics and telecom installers. 5G, CCTV and smart-home demand rising."),
"751": (3,5,6,4,"stable","Food processing is partly automatable in factories; artisanal work stays manual.","Bakers, butchers and food processors. PLI for food processing pushes mechanisation in organised units."),
"752": (3,4,5,4,"stable","Woodwork and carpentry are manual crafts; CNC affects organised furniture units.","Carpenters and cabinet makers. Furniture demand steady; mostly informal workshops."),
"753": (3,6,6,4,"declining","Garment work is repetitive and increasingly automatable, though India's low wages slow it.","Tailors and garment workers. India's largest manufacturing employer after agriculture; export units mechanising."),
"754": (3,4,5,4,"stable","Miscellaneous crafts are manual; AI plays little role.","Other craft workers. Diverse traditional and modern trades, largely informal."),
# ── 8 Plant & Machine Operators ─────────────────────────────
"811": (3,6,6,2,"stable","Mining-plant operation is partly automatable; heavy machinery and safety keep humans on-site.","Mining and mineral-plant operators. Coal and ore; Coal India is a major formal employer."),
"812": (4,6,6,2,"stable","Metal-processing operation is increasingly automated in modern plants.","Metal-processing operators. Steel and aluminium; organised, often unionised."),
"813": (4,6,6,2,"stable","Chemical and photo-plant control is automatable via sensors and AI.","Chemical and pharma plant operators. India's pharma and chemicals strength sustains demand."),
"814": (4,6,6,2,"stable","Rubber, plastic and paper machine operation is repetitive and automatable.","Rubber, plastic and paper machine operators. Packaging and auto-component demand."),
"815": (4,7,6,2,"declining","Textile-machine operation is highly repetitive and a prime automation target.","Textile and garment machine operators. Tiruppur and Surat clusters; automation pressure rising."),
"816": (4,6,6,3,"stable","Food-machine operation is partly automatable in organised plants.","Food and beverage machine operators. Processed-food growth sustains demand."),
"817": (4,6,5,2,"stable","Wood and paper plant operation is repetitive and automatable.","Wood and paper plant operators. Pulp, paper and board manufacturing."),
"818": (4,6,5,2,"stable","Other plant operation is structured and partly automatable.","Other stationary-plant operators across industries."),
"821": (4,7,6,3,"stable","Assembly is repetitive and a leading robotics target, though India's wages slow adoption.","Assemblers in electronics, auto and appliances. PLI-driven manufacturing expands these jobs for now."),
"831": (4,5,7,1,"stable","Locomotive driving is being automated abroad, but Indian rail keeps drivers for safety and scale.","Locomotive drivers and rail operators. Indian Railways is among the world's largest employers; secure formal jobs."),
"832": (3,5,6,8,"growing","Driving is physical; full automation is far off in India, while apps reshape the work.","Car, taxi and van drivers. Ola and Uber platformised the trade; over 50 lakh app-based drivers."),
"833": (3,5,5,5,"stable","Truck and bus driving stays human in India for decades; AI assists routing only.","Truck and bus drivers. Backbone of freight and transit; chronic driver shortage despite demand."),
"834": (3,6,6,3,"growing","Mobile-plant operation is partly automatable; site work keeps operators in the cab.","Crane, excavator and earthmover operators. Infra boom drives strong demand."),
# ── 9 Elementary ────────────────────────────────────────────
"911": (2,3,5,5,"stable","Cleaning is physical service work AI cannot perform; apps digitise booking.","Domestic workers and cleaners. A vast, deeply informal, mostly female workforce; platforms like BroomBerg emerging."),
"912": (2,4,5,5,"stable","Vehicle and window cleaning is manual; AI plays no role.","Vehicle and window cleaners. Car-wash apps add some gig structure."),
"921": (1,2,4,2,"declining","Agricultural labour is physical, seasonal outdoor work outside AI's reach.","Agricultural and fishery labourers. Landless workers; MGNREGA is the key safety net for this group."),
"931": (1,3,5,3,"growing","Construction labour is physical; AI and prefab touch planning, not the work.","Mining and construction labourers. Migrant-heavy; e-Shram registration is the main formalisation effort."),
"932": (2,5,6,3,"stable","Manufacturing labour is repetitive and a medium-term automation target.","Manufacturing helpers and labourers. Factory-floor entry jobs; PLI sustains demand for now."),
"933": (2,4,6,5,"growing","Loading and warehouse labour is partly automatable; e-commerce reshapes it.","Transport and warehouse loaders. E-commerce and logistics boom (Delhivery, Amazon) drives demand."),
"941": (2,4,5,6,"growing","Kitchen-helper work is physical; cloud kitchens add platform structure.","Food-preparation assistants. QSR and cloud-kitchen growth; largely informal."),
"951": (2,3,5,5,"stable","Street services are physical; UPI digitises payment only.","Street service workers: shoe-shiners, repairers, vendors. Deeply informal urban livelihoods."),
"952": (2,3,5,5,"stable","Non-food street vending is physical; UPI and ONDC touch payment and reach.","Non-food street vendors. PM SVANidhi and ONDC aim to formalise parts of the trade."),
"961": (2,4,6,3,"stable","Refuse collection is physical; AI affects route planning, not collection.","Sanitation and refuse workers. Swachh Bharat raised visibility; safai karamcharis remain socially vulnerable."),
"962": (3,4,6,8,"fast-growing","Delivery work is physical, but it is the most platformised job in India, born on apps.","Delivery riders and elementary platform workers. Over 1 crore gig workers; Swiggy, Zomato, Amazon, Blinkit. NITI Aayog projects 2.35 crore by 2030."),
}
