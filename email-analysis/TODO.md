Data
====
18:22:23      flavius | sunt tot felul de scule pentru interoperarea cu mutt                                                  │
18:22:30      flavius | sau mutt, da                                                                                          │
18:22:35      flavius | si ai acolo Maildir                                                                                   │
18:22:43      flavius | faci un label in gmail, bagi un filtru                                                                │
18:22:49      paullik | pai ok, dar cum iau eu toate mail-urile din google groups, ca aici ma doare                           │
18:22:55      flavius | si setezi mutt sa descarce acel label ca un maildir                                                   │
18:24:05      flavius | paullik: tu ai treaba cu grupul google, nu esti abonat la grup si primesti instantaneu mailurile la   │
                      | tine in gmail?                                                                                        │
18:24:24      flavius | paullik: pai cauti si tu in gmail pe interfata web a lor                                              │
18:24:32      flavius | from: yap@googlegroups.com                                                                            │
18:24:39      flavius | sau to: ...                                                                                           │
18:24:56      flavius | si gasesti ditamai carul de mailuri, toate despre YAP                                                 │
18:25:03      flavius | si le bagi acel label                                                                                 │
18:25:12      flavius | toate acestea in gmail, pe web                                                                        │
18:25:19      flavius | si apoi treci la mutt                                                                                 │
18:25:36      flavius | ai toate mailurile in gmail, nu?                                                                      │
18:25:46      paullik | da                                                                                                    │
18:25:52      flavius | pai vezi                                                                                              │
18:26:20      flavius | trebuie doar sa le cauti si sa te asiguri ca au toate labelul "phpro" de exemplu                      │
18:28:48      flavius | mergi linistit pe maildir si plain text :)                                                            │
18:30:53      flavius | daca oricum le parsezi, poti sa le si salvezi pe toate si sa le faci cache                            │

What I need
===========
* http://docs.python.org/3/library/email.parser.html
* Only the timespan between the PR request and the PASS response.
* Care not to confuse something like `am primit pass?` with the actual pass,
  here I could validate the email address with a whitelist (tutors) and, for
  safety, a blacklist (the email who requested PR)
