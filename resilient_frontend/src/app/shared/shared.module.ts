import { NgModule, importProvidersFrom } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from './material/material.module';
import { LayoutModule } from './layout/layout.module';
import { PrimengModule } from './primeng/primeng.module';
import { TruncateDecimalPipe } from './pipes/truncate-decimal.pipe';

@NgModule({
  declarations: [
    TruncateDecimalPipe
  ],
  imports: [
    CommonModule,
    MaterialModule,
    LayoutModule,
    PrimengModule
  ],
  exports: [
    MaterialModule,
    LayoutModule,
    PrimengModule,
    TruncateDecimalPipe
  ],
  providers: [
    importProvidersFrom(PrimengModule)
  ]
})
export class SharedModule { }
