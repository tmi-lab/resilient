import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LocalStorageService {

  constructor() { }

  setData(key: string, data: any): void {
    const stringData = JSON.stringify(data);
    localStorage.setItem(key, stringData);
  }

  getData(key: string): any {
    const stringData = localStorage.getItem(key);
    return stringData ? JSON.parse(stringData) : null;
  }

  clearData(key: string): any {
    localStorage.removeItem(key);
  }
}
