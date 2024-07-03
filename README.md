# Tracking people on security camera between frames using the Hungarian Method

## Assignment Problem Solution

The assignment of detected objects between frames was performed using a graph-solving algorithm - the Hungarian Method. This method is implemented in the code using the linear_sum_assignment function from the scipy library.

## Scoring Determination for the Graph

To determine the scoring that indicates the similarity between detected objects in the image, the following information available in the input data was used:

  - The distance between detected objects
  - The color histogram within the ROI defined by the coordinates of the bounding box surrounding the object
  - The object's height relative to the height of the image

These parameters were compared for all objects from two consecutive frames and summed. The parameter values were transformed to indicate the relationship between frames, i.e., for histograms, it is the correlation, and for distance and height, it is the absolute value of the difference. The smaller the score, the higher the probability that the person in the next frame is the same as in the previous one.

## Cost Matrix

The cost matrix has a shape dependent on the number of objects found in the image, where the number of rows equals the number of objects detected in the first frame, and the number of columns equals the number of objects detected in the second frame. Each element of the matrix is the similarity score between a given object from the first frame and the second frame.

However, the function used to compute the graph does not solve certain problems:

  - The number of people in the frames is the same, but they are not the same individuals. To solve this problem, a color histogram correlation parameter was added and a threshold was set above which an object is classified as new.
  - The number of people in the frames is the same and greater than 2. In such a situation, the Hungarian method may return an object that does not have the smallest score due to the matrix's dimension and the need to unmark columns and rows. Here, the solution was to artificially add an extra row to the matrix, which cannot pass the limiting threshold.

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
