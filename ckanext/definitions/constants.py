# TODO add Loes Link in HTML
#                   'Voor meer instructies, is er een module beschikbaar in Loes --> https://gemeentedenhaag.trainingscatalogus.nl/nl/app#/course/76d0bb0e-cec9-4901-9391-bc58bfcf8e2d<br><br>' \

EMAIL_SIGNATURE = '<br><br><br>' \
                  'Voor meer instructies, is er een module beschikbaar in <a href="https://gemeentedenhaag.trainingscatalogus.nl/nl/app#/course/76d0bb0e-cec9-4901-9391-bc58bfcf8e2d">Loes</a> <br><br>' \
                  'Met vriendelijke groet,<br><br>' \
                  'Functioneel Beheer Datacatalogus<br>' \
                  'databibliotheek@denhaag.nl<br><br>' \
                  '' \
                  'Gemeente Den Haag<br>' \
                  'Bedrijfsvoeringsexpertisecentrum (BEC)<br>' \
                  'Spui 70<br>' \
                  '2511 BT Den Haag<br>' \
                  'www.denhaag.nl<br><br>' \
                  '' \
                  'De disclaimer van toepassing op e-mail van de gemeente Den Haag vindt u op: http://www.denhaag.nl/disclaimer'

EMAIL_DELETE_DEFINITION_SINGLE = {"subject": "Gelinkte definitie verwijderd",
                                  "message": "Beste collega,<br><br>"
                                             "De definitie '{0}' die gelinkt was aan "
                                             "de vermelding '{1}', waarvan u de eigenaar of gemandateerde bent, is gedeactiveerd c.q. verwijderd.<br>"
                                             "Link naar vermelding --> {2}" + EMAIL_SIGNATURE
                                  }

EMAIL_DELETE_DEFINITION_MULTI = {"subject": "Gelinkte definitie verwijderd",
                                 "message": "Beste collega,<br><br>"
                                            "U bent de eigenaar of gemandateerde van meerdere vermeldingen met een gelinkte definitie die is gedeactiveerd c.q. verwijderd.<br>"
                                            "Het gaat om de definitie {0} die was gekoppeld aan de volgende vermeldingen:<br>"
                                            "{1}"
                                            + EMAIL_SIGNATURE
                                 }
