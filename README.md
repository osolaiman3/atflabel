# ATF label scanner

Single server website utilizing a REST endpoint to interface with the OCR and do text comparisons from extracted text

## Use
- Fill out form with respective data
  - Brand Name
  - Product Class/Type
  - Alcohol Content in % (allow for entry of the %)
    - Can show up as ABV, Alc./Vol., 
  - Net contents 
    - ml/fl oz/L
        - Large bottles may use 1.5L or more, must be accounted for
 - Upload image(s) via drag/drop or filesystem
 - Submit for a confirmation screen
 - Obtain Results of what the label(s) have and their location

## Approach

### UI
- Minimize badly formatted inputs
    - use drop downs for 'standard' values (ml,L,fl oz)
    - restrict valid inputs to valid characters (regex/numbers only in some fields)
    - character limits to fields
- Clarity of actions
    - submit should be prominent
    - segments of related things should be close to each other
- Minimize frustration
    - user should not have to re-enter the same data
    - modification of data should be easy
- Some bugs are known to make things less pleasing to see, but none that make the capbility unusable. Deemed suitable as an MVP. 
    - Many found require breaking the limitations 

###  OCR Capabilities
- Chose a combination of tesseract and CRAFT text detector. This was in contrast with using better 3rd party APIs. Goal is to detect multiple text orientations, keep track of their location and check for text validation.

- Drawbacks
    - slower processing times
    - May miss things better resources like google vision may have
- Pros
    - 3rd party APIs cannot be abused and keys cannot be taken if they are not in use
    - cost of running the models is less than utilizing third parties 

### Security
- Form sanitization 
- upload limitations for image (filetypes, file size)
    - File can be further sanitized by modifying image with noise to destroy embedded data
- Container security
    - minimizing held data, everything is in active memory. Anything processed should be gone when out of scope. 
    - minimizing what is on the container other than what is needed to run the webserver

## Follow ups:

### UI/capabilities
#### Label location highlighting 
Base OCR 

#### multiple images
Many labels aren't in one piece, they come in multiple pieces. This should allow for applicants to submit labels as they have them designed instead of having to also compile them into a single image for upload


### Database of submitted forms to look up against

#### Indexing/Lookup: 
Lookup indexing based on "unique" key word examples

    Whisky
    Rum
    Vodka

And for beer

    Lager
    IPA/India Pale Ale
    Stout

And Wine 

    Zifandel
    Riesling
    Port

possible conflicts: some cocktails and drinks may have multiple index classifiers in their name: "Whisky Sour" vs "Whisky" or "Sour beer" for example

Solve by using last instance of a keyword making assumption of Adjective-Noun language structure? 

- Matters more for cutting down how many alcohol products are being checked against than being specific to the real type of alcohol (not a database being used for public verifications). Can still result in collisions like Whisky Sour. May result in many types of Ales being consolidated (Pale Ale, Amber Ale, etc)

### Architecture

Containerization of this service should allow for consistency and scalability of the service. This application is effectively a "verification service" as part of a larger alcohol product approval system. The web app section is more of a test UI for it than part of a scalable product. 

#### Separation of services

Number of requests matter. There should not be a lot of requests to the system (manual insertion/verification before putting it into the database). 

However, an "audit" may occur which may need to be distributed to many OCR services. Queuing via a service like Apache Kafka may be a good move in such a case. OCR verification can be done via instances of this webserver without a GET for the webpage. Should allow for many services to be scaled up with the demand for audit of all data

Queued correctly, should allow for many ttb submissions to be run in parallel. 