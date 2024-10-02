// src/app/services/env.service.ts
import { Injectable } from '@angular/core';
import { AppConfig } from '../shared/models/app-config';

@Injectable({
  providedIn: 'root',
})
export class EnvService {
  public appConfig: AppConfig = {
    apiUrl: '0.0.0.0',
    chartFields: {
      scale: [],
    },
    nullReplaceValue: 0,
  };

  constructor() {
    const env = (window as any).__env;

    if (env) {
      this.appConfig = Object.assign({}, env);
    }
  }
}
