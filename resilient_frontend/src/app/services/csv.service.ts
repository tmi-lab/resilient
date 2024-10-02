import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class CsvService {

  constructor() { }

  generateCSV(deviceSummary: any): string {
    const { labels, datasets } = deviceSummary.chartData;
    let csvContent = 'Date,' + datasets.map((dataset: any) => dataset.label).join(',') + '\n';

    for (let i = 0; i < labels.length; i++) {
      const row = [labels[i]];
      for (let j = 0; j < datasets.length; j++) {
        row.push(datasets[j].data[i] === null ? -1 : datasets[j].data[i]);
      }
      csvContent += row.join(',') + '\n';
    }

    return csvContent;
  }

  downloadCSV(deviceSummary: any, filename: string = 'data.csv'): void {
    const csvContent = this.generateCSV(deviceSummary);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}
