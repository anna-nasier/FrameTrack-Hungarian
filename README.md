# SIwR-projekt

## Rozwiązanie problemu przypisania

Przypisywanie wykrytych obiektów pomiędzy klatkami zostało wykonane z użyciem algorytmu rozwiązywania grafów - Metody Węgierskiej. Jest ona zaimplementowana w kodzie poprzez użycie funkcji z biblioteki scipy, o nazwie **linear_sum_assignment**. 

## Wyznaczanie punktacji do grafu

Aby wyznaczyć punktację określającą podobieństwo między obiektami wykrytymi na obrazie wykorzystano następujące informacje dostępne w danych wejściowych: 

- dystans pomiędzy pomiędzy wykrytymi obiektami 
- histogram barw w roi wyznaczonym przez współrzędne prostokąta otaczającego obiekt 
- wysokość obiektu względem wysokości obrazu.

Wymienione parametry zostały porównane dla wszystkich obiektów z dwóch klatek następujących po sobie oraz zsumowane. Wartości parametrów są przekształcone tak, aby wskazywały zależność pomiędzy klatkami, tzn. dla histogramów jest to korelacja, a dla dystansu i wysokości wartość bezwzględna różnicy. Im mniejsza punktacja tym większe prawdopodobieństwo, że osoba na następnej klatce jest ta sama co na poprzedniej.  

## Macierz kosztów 

Macierz kosztów ma kształt zależny od ilości obiektów znalezionych w obrazie, gdzie liczba rzędów równa jest ilości obiektów wykrytych na pierwszej klatce, a liczba kolumn ilości obiektów wykrytych na klatce drugiej. Każdy element macierzy to punktacja podobieństwa pomiędzy danym obiektem z klatki pierwszej do klatki drugiej. 

Sama funkcja użyta do obliczenia grafu nie rozwiązuje jednak pewnych problemów: 

- liczba osób na klatkach jest ta sama, ale nie są to te same osoby - w celu rozwiązania tego problemu dodano parametr korelacji histogramu barw oraz wyznaczono próg, powyżej którego obiekt zostaje sklasyfikowany jako nowy
- liczba osób na klatkach jest ta sama i wyższa niż 2 - metoda węgierska w takiej sytuacji może zwrócić jako wynik obiekt, który nie ma najmniejszej punktacji ze względu na wymiar macierzy i konieczność odznaczania kolumn i rzędów - tutaj rozwiązaniem było sztuczne dodanie dodatkowego rzędu do macierzy, który nie jest w stanie przejść przez próg ograniczający 