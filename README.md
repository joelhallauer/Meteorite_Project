# 🌍 Impact Atlas – Meteoriten weltweit

Ein webbasiertes Dashboard zur Visualisierung und Analyse von Meteoriteneinschlägen weltweit. Dieses Projekt basiert auf dem NASA-Datensatz [Meteorite Landings](https://www.kaggle.com/datasets/nasa/meteorite-landings).

## 💡 Motivation & Grundidee

Die zentrale Motivation für den "Impact Atlas" war die Entwicklung eines webbasierten Dashboards, das Datenvisualisierung, interaktive Filterung und geografische Verortung kombiniert, um Meteoritenfunde weltweit darzustellen und analysierbar zu machen.

## 🎯 Projektziele

* **Entwicklung eines webbasierten Dashboards**: Erstellung einer interaktiven Plattform zur Erkundung von Meteoritendaten].
* **Kombination von Datenvisualisierung, interaktiver Filterung und geografischer Verortung**: Bereitstellung vielfältiger Möglichkeiten zur Datenexploration.
* **Darstellung aller Meteoritenfunde auf einer interaktiven Weltkarte**: Visualisierung der geografischen Verteilung von Meteoriteneinschlägen.
* **Filterung nach Masse, Jahr, Meteoritentyp und Fundstatus**: Ermöglichung detaillierter Analysen der Daten.
* **Statistische Auswertung**: Zusammenfassung von Trends und Mustern (z.B. Anzahl der Meteoriten, Durchschnitts- und größte Masse, Zeitraum).
* **Benutzerfreundliches, interaktives Interface**: Gestaltung einer intuitiven Oberfläche für eine einfache Bedienung.

## ❓ Forschungsfragen

Das Dashboard wurde entwickelt, um folgende Fragen zu beantworten und explorative Analysen zu ermöglichen:

1.  Welche Regionen zeigen besonders viele Meteoritenfunde?
2.  Welche Meteoritentypen kommen am häufigsten vor?
3.  Wie hat sich die Anzahl der Meteoritenfunde über Jahrzehnte verändert?

## 📊 Visualisierungswerkzeuge & Interaktion

Das Dashboard bietet verschiedene Visualisierungsoptionen und Interaktionstechniken:

* **Geografische Visualisierung**: Weltkarte mit verschiedenen Darstellungsformen:
    * **Cluster-Karten**: Gruppierung von nahegelegenen Einschlägen für eine bessere Übersicht.
    * **Punktkarten**: Einzelne Darstellung jedes Meteoritenfundes.
    * **Heatmaps**: Darstellung von Hotspots und Dichtebereichen von Einschlägen.
    * **Farbcodierung nach Jahr**: Visuelle Unterscheidung der Funde basierend auf dem Einschlagsjahr.
* **Statistische Zusammenfassungen**: Anzeige relevanter Metriken wie Anzahl der Meteoriten, durchschnittliche Masse, größte und kleinste Masse sowie der analysierte Zeitraum.
* **Diagramme für Trends**: Visualisierung von zeitlichen Entwicklungen.
* **Interaktive Filter**:
    * **Masse**: Filterung nach einem Massenbereich in Gramm.
    * **Meteoritentyp**: Auswahl spezifischer Meteoritentypen.
    * **Jahr**: Auswahl eines Zeitraums für die Meteoritenfunde.
    * **Status (Fall/Found)**: Unterscheidung zwischen beobachteten Fällen und gefundenen Meteoriten.
    * **Ortssuche & Suchradius**: Ermöglicht die Suche nach Meteoriten in einem bestimmten geografischen Bereich um einen Ort herum.

## 🛠️ Technischer Aufbau

* **Programmiersprache**: Python
* **Framework**: Dash by Plotly
* **Visualisierung**: Plotly Express
* **Datenverarbeitung**: Pandas

## 🚀 Zukünftige Ideen

* Erweiterte Analysefunktionen und zusätzliche Diagramme.
* Integration weiterer Datenquellen.
* Verbesserung der Performance bei sehr großen Datensätzen.
