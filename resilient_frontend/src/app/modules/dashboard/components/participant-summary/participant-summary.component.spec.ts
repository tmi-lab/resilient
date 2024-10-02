import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParticipantSummaryComponent } from './participant-summary.component';

describe('ParticipantSummaryComponent', () => {
  let component: ParticipantSummaryComponent;
  let fixture: ComponentFixture<ParticipantSummaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ParticipantSummaryComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ParticipantSummaryComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
