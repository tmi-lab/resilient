import { NgModule, importProvidersFrom } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardComponent } from './dashboard.component';
import { DashboardRoutingModule } from './dashboard-routing.module';
import { ParticipantsComponent } from './components/participants/participants.component';
import { ReportsComponent } from './components/reports/reports.component';
import { DevicesComponent } from './components/devices/devices.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { ParticipantSummaryComponent } from './components/participant-summary/participant-summary.component';
import { SharedModule } from './../../shared/shared.module';
import { MessageService } from 'primeng/api';


@NgModule({
  declarations: [
    DashboardComponent,
    ParticipantsComponent,
    ReportsComponent,
    DevicesComponent,
    ParticipantSummaryComponent,
  ],
  imports: [
    CommonModule,
    DashboardRoutingModule,
    SharedModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [
    importProvidersFrom(SharedModule),
  ]
})
export class DashboardModule { }
