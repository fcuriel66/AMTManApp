# AMTMan App
AMTMan is an AI Aircraft Maintenance Task Manager. 
Aircraft Maintenance is a documentation intensive and time consuming endevour that demamd lots of engineer and technician resources. AMTMan automates a significant part of this process through LLM based agents and RAG's, a bit of SQL and using the reliable tool Streamlit for the UI.

## General Project Description

A significant and valuable time of the technicians/engineers time in a MRO operation is wasted searching and picking the right information for the maintenance/repair tasks in a complex Jet Aircraft. If an AI prompted and driven query could do this automatically it could save a significan amount of time for the technicians even if it is not 100% accurate and the repair shop could speed the delivery of serviced/repaired aircraft up to 30-50%.


- Compiles the Manufactrurer's Maintenance and Service Manuals into a database accesible to a LLM for RAG processing and embedding.
- Uses a chat interface with the technical personnel where the user provides either the problematic symptoms the aircraft presents or the system and or components that the technicians suspect to be causing the problem.
- The agent-based LLM then decides and searches the embeddings to find all the tasks relevant to the problem or the service required.
- The pdf manual files are copied into a directory for printing or referencing while working in the aircraft serviced.
- The whole time-stamped history of every chat and user involved is preserved in a SQLite local database for future reference.


## What problem does it solve?

When a complex jet aircraft needs service or repair, the technicians should have the proper materials to work on the aircraft but also the proper service/repair manual information. There are industry standards for manual information classification but the reality is that every manufacturer has its own philosophy about their manuals logic and structure. That is why the searching for the proper tasks before even starting working on the aircraft, usually requires the flexibility of a human agent. This labor is time consuming because the information for a service and even for a repair could be in many different parts of the manual or even in a different manual (e.g. airplane or engine, etc.). So it is a problem when the time for this search for all the proper documents is comparable to the time that the service or repair is of the same order of magnitude. The proposed solution here, is to exploit the capabilities of an AI agent so that the production of the required documents is completed in minimal time. The proposed scheme is not limited by a simple initial general query (though that would be ideal in some cases) but could consist in a couple of iterations after the initial material is generated. The latter would be probably common since some tasks will require a search in semantically distant manuals.
