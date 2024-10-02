import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../material/material.module';
import { FooterComponent } from './components/footer/footer.component';
import { HeaderComponent } from './components/header/header.component';
import { PrimengModule } from '../primeng/primeng.module';
import { SummaryCardComponent } from './components/summary-card/summary-card.component';



@NgModule({
  declarations: [
    FooterComponent,
    HeaderComponent,
    SummaryCardComponent
  ],
  imports: [
    CommonModule,
    MaterialModule,
    PrimengModule
  ],
  exports: [
    HeaderComponent,
    FooterComponent,
    SummaryCardComponent,
    PrimengModule
  ]
})
export class LayoutModule { }
