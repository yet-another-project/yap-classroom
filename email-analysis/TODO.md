* Inspect the code that does the analyses and DRY it


22:52:02   @flavius | o istograma poti sa faci?                                                                                 │
22:52:26   @paullik | histograma a ce?                                                                                          │
22:52:33    +Paul92 | numarul de exercitii nu ar fi util, eventual pe fiecare exercitiu timpul necesar?                         │
22:52:43   @paullik | Paul92, aia e mai greu                                                                                    │
22:52:57   @paullik | ca nu pot extrage numele exercitiului din toate mailurile                                                 │
22:53:08   @paullik | ca fiecare a pus cum l-a taiat capul                                                                      │
22:53:18   @flavius | paullik: pe axa x numarul de zile, pe y numarul in procente ale PR-urilor care au durat X zile pana la    │
                    | pass                                                                                                      │
22:53:24    +Paul92 | paullik: asta asa e. desi putem normaliza cumva
22:53:29   @flavius | paullik: si medianul mai e util in statistica                                                             │@  
22:53:42    +Paul92 | pot sa fac in gist foldere? adica stiu ca pot dar se supara cineva?                                       │@
22:53:55   @flavius | deci ... media e mai buna acum, ca suspectez ca e o distributie gauss                                     │@   
22:54:08   @paullik | flavius, o distributie de care?                                                                           │+
22:54:10   @flavius | Paul92: poti                                                                                              │+ 
22:54:16   @flavius | normala, gauss                                                                                            │ 
22:55:10   @paullik | flavius, fac histograma, dar medianul? ce e ala in contextul histogramei de care vorbim?                  │ 
22:55:35   @paullik | ca la median m-as gandi cum a evoluat media nr de ore o data cu cererile de pr                            │
22:56:00   @paullik | dar in contextul histogramei chiar nu-mi dau seama                                                        │
22:56:20   @flavius | pai ar fi un indicator preliminar daca avem outliers, daca medianul e departe de medie, ar insemna ca     │
                    | distributia are skewness                                                                                  │
22:56:34   @paullik | o da                                                                                                      │
22:56:37   @paullik | nu mia inteleg nimic                                                                                      │
22:56:41   @paullik | dar e bine                                                                                                │
22:56:43   @paullik | invat                                                                                                     │
22:56:48   @flavius | si atunci am inspecta mai indeaproape cum sunt distribuite                                                │
22:57:01   @flavius | vorbeam acum ca idee general utila, nu doar in acest caz                                                  │
22:57:24   @flavius | outlier = data point far outside on the plot, isolated                                                    │
22:57:31   @paullik | :))                                                                                                       │
22:57:35   @paullik | fix ce stiam mi-ai explicat                                                                               │
22:57:35   @flavius | skewness = strambitate                                                                                    │
22:57:43   @flavius | cat de stramba e distributia                                                                              │
22:57:57   @flavius | in mod normal aia gauss e simetrica                                                                       │
22:58:01   @paullik | aha, skewness, are sens adica numele e sugestiv                                                           │
22:58:18   @flavius | daca nu e simetrica, nu e gauss :)                                                                        │
22:59:56   @paullik | bun, hai ca salvez separat ce ai zis aici, for reference                                                  │
23:00:03   @paullik | si ma mai documentez                                                                                      │
23:00:19   @paullik | deci ar fi util sa fac histograma si median (ce-o fi ala/aia)                                             │
23:00:46   @flavius | median = asezi numerele sortate in array                                                                  │
23:00:56   @flavius | si medianul este cel aflat la jumatatea array-ului                                                        │
23:01:33   @paullik | daca n = 2k+1? :))                                                                                        │
23:01:35   @flavius | daca numerele sunt uniform distribuite, e probabil sa fie aproape de medie                                │
23:01:47   @flavius | in acel caz se face media                                                                                 │
23:01:52   @flavius | intre cele doua                                                                                           │
23:01:57   @paullik | a, deci e buna intreabrea :D                                                                              │
23:02:27   @flavius | intrebarea si mai buna e: cand te ghidezi dupa medie, si cand dupa median? :D                             │
23:02:42   @flavius | iti las tie tema de gandire, e logica treaba                                                              │
23:02:43   @paullik | aha, de acolo skewness, ca sunt aproape de medie adica putin deformate si invers                          │
23:02:55   @paullik | stai sa inteleg prima data mai bine termenii si dupa                                                      │
23:03:11   @paullik | ma ghidez ca sa analizez ce?                                                                              │
23:03:20   @paullik | asta as intreba prima data                                                                                │
23:03:49   @flavius | cand spune media ceva reprezentativ despre data set, si cand medianul?                                    │
23:04:05   @paullik | hmm, o sa ma gandesc                                                                                      │
23:04:28   @paullik | asa ce-mi trece acum prin minte:                                                                          │
23:04:36   @paullik | medianul la un element e chiar elementul                                                                  │
23:04:42   @paullik | la doua elemente e chiar media                                                                            │
23:04:58   @paullik | si ramane sa ma gandesc mai mult la un set de date mare 
