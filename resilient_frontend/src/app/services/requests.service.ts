import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Users, Devices } from '../shared/models/database-types';
import { ICONS } from '../shared/constants/icons'
import { EnvService } from './env.service';

@Injectable({
  providedIn: 'root'
})
export class RequestsService {

  private icons = ICONS;
  private baseUrl: string;

  constructor(
    private http: HttpClient,
    private _envService: EnvService
  ) {
    this.baseUrl = this._envService.appConfig.apiUrl;
  }

  addParticipant(participantData: any): Observable<any> {
    const reqUrl = this.baseUrl + 'users/';

    return this.http.post<any>(reqUrl, participantData);
  }

  editParticipant(participantData: any): Observable<any> {
    const reqUrl = this.baseUrl + 'user/' + participantData.userId + '/';

    // if (Object.keys(participantData).length  2) {
    //   return this.http.put<any>(reqUrl, participantData);
    // }

    return this.http.patch<any>(reqUrl, participantData);
  }

  getUsers(): Observable<Users> {
    const usersUrl = this.baseUrl + 'users/';

    return this.http.get<Users>(usersUrl);
  }

  getDevices(): Observable<Devices> {
    const usersUrl = this.baseUrl + 'devices/';

    return this.http.get<Devices>(usersUrl);
  }

  getDevicesByUsername(username: string): Observable<any>{
    const devicesUrl = this.baseUrl + 'devices/?username=' + username;

    return this.http.get<any>(devicesUrl);
  }

  getDeviceSummaryByUsername(username: string, device_type: string): Observable<any>{
    const devicesUrl = this.baseUrl + this.icons[device_type].summaryUrl + '?username=' + username;

    return this.http.get<any>(devicesUrl);
  }

  saveWithingsCredentials(participantWithingsData: any): Observable<any> {
    const reqUrl = this.baseUrl + 'reports/withings-credentials/';

    return this.http.post<any>(reqUrl, participantWithingsData);
  }

}
