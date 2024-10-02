import { ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild, Renderer2 } from '@angular/core';
import { RequestsService } from 'src/app/services/requests.service';
import { Role } from '../../../../shared/models/roles';
import { User, Users } from '../../../../shared/models/database-types';
import { NgModel, ValidatorFn } from '@angular/forms';
import { Router } from '@angular/router';
import { ICONS } from '@shared/constants/icons';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ConfirmationService } from 'primeng/api';
import { EnvService } from 'src/app/services/env.service';
import { ChartField, DeviceField, DeviceType } from '@shared/models/app-config';
import { UIUtilsService } from 'src/app/services/ui-utils.service';
import { CsvService } from 'src/app/services/csv.service';
import { LocalStorageService } from '@app/services/local-storage.service';

@Component({
  selector: 'app-participants',
  templateUrl: './participants.component.html',
  styleUrl: './participants.component.scss'
})
export class ParticipantsComponent implements OnInit {
  @ViewChild('chart') chart: any;

  currentParticipant: any;
  deviceSummary: any;
  deviceName: string = '';
  deviceDetailsVisible: boolean[] = [];
  editParticipantForm: FormGroup;
  filteredParticipants: User[] = [];
  icons = ICONS;
  isAddParticipantSuccessful: boolean = false;
  isDuplicateUsername: boolean = false;
  participantData: any;
  participantForm: FormGroup;
  participants: User[] = [];
  nullReplaceValue: number;
  roles: Role[] = [];
  selectedRole: Role | undefined;
  selectedRows: any[] = [];
  showDialog: boolean = false;
  showEditDialog: boolean = false;
  showParticipantSummaryDialog: boolean = false;
  showDeviceTableDialog: boolean = false;
  showSpinner: boolean = false;
  username: string;
  usernameFilter: string = '';
  withingsAuthURL: string = ''
  chartFields: ChartField;
  chartVisualizationOptions: any[] = [
    {label: 'Last Week', value: 'last_week'},
    {label: 'Last Month', value: 'last_month'},
    {label: 'Last 3 Months', value: 'last_3_months'},
    {label: 'Last Year', value: 'last_year'},
    {label: 'All Time', value: 'all_time'}
  ];
  dataVisualizationOptions: any[] = [
    {label: 'Table', value: 'table', icon: 'pi pi-table'},
    {label: 'Graph', value: 'graph', icon: 'pi pi-chart-bar'}
  ]
  defaultVisualizationOption: string = 'all_time';
  defaultDataVisualizationOption: string = 'graph';
  @ViewChild('usernameInput', { static: false }) usernameInput?: NgModel;

  selectedColumns: any[] = [];
  maxColumnWidth: number = 200;

  constructor(
    private _requestsService: RequestsService,
    private _envService: EnvService,
    private _uiUtilsService: UIUtilsService,
    private _csvService: CsvService,
    private _router: Router,
    private _fb: FormBuilder,
    private _confirmationService: ConfirmationService,
    private _localStorageService: LocalStorageService,
    private _changeDetectorRef: ChangeDetectorRef,
    private _renderer: Renderer2,
    private _elementRef: ElementRef
  ) {

    this.roles = [
      {name: 'study-participant'},
      {name: 'study-partner-participant'},
      {name: 'test'}
    ];

    this.username = '';

    this.participantForm = this._fb.group({
      username: ['', [Validators.required, Validators.minLength(4)]],
      selectedRole: ['', Validators.required]
    });
    this.editParticipantForm = this._fb.group({
      username: ['', [Validators.minLength(4)]],
      selectedRole: ['']
    });

    this.chartFields = this._envService.appConfig.chartFields;
    this.nullReplaceValue = this._envService.appConfig.nullReplaceValue;
  }

  ngOnInit(): void {
    this.getUsers();
    this.calculateMaxColumnWidth();
    window.addEventListener('resize', this.calculateMaxColumnWidth.bind(this));
  }

  calculateMaxColumnWidth() {
    this.maxColumnWidth = 0.8 * window.innerWidth/(this.selectedColumns.length+1);
    document.documentElement.style.setProperty('--maxColumnWidth', this.maxColumnWidth + 'px');

  }

  getUsers(): void{
    this._requestsService.getUsers().subscribe({
      next: (answer: Users) => {
        if (answer) {
          const usersArray: User[] = Object.values(answer.users);
          this.participants = usersArray.filter( user => {
            const role = user['role'].toLowerCase();
            const active = user['active'];
            return role !== 'admin' && role !== 'clinician' && role != 'super_admin' && active;

          });
          this.filteredParticipants = this.participants;
        }
      }
    });
  }

  applyUsernameFilter(): void {
    this.filteredParticipants = this.participants.filter(participant => {
      return participant.username.toLowerCase().includes(this.usernameFilter.toLowerCase());
    });
  }

  onUsernameInputChange(): void {
    this.isDuplicateUsername = false;
    this.isAddParticipantSuccessful = false;
  }

  showAddParticipantModal(): void {
    this.showDialog = true;
    if (this.usernameFilter) {
      this.username = this.usernameFilter
    }
  }

  showEditParticipantModal(): void {
    this.showEditDialog = true;
  }

  addParticipant(): void{

    if (this.participantForm.invalid ){
      this.participantForm.markAllAsTouched();
      return;
    }

    this.showSpinner = true;

    const participantData = {
      username: this.participantForm.value.username,
      role: this.participantForm.value.selectedRole.name,
      password_hash: "NA"
    }
    console.log(participantData);

    this._requestsService.addParticipant(participantData).subscribe({
      next: (response) => {
        this.showSpinner = false;
        this.isAddParticipantSuccessful = true;
        this._localStorageService.setData('participant', response);
      },
      error: (error) => {
        this.isDuplicateUsername = error.error.username.status_code = 403 ? true : false;
        this.showSpinner = false;
        console.log(error);

      }
    }
    );
  }

  editParticipant(): void{
    const formData = this.editParticipantForm.getRawValue();
    formData.selectedRole = formData.selectedRole ? formData.selectedRole.name : '';

    if (!Object.values(formData).some(value => value !== '' || value !== null || value !== undefined)) {
      return;
    }

    if (this.editParticipantForm.invalid ){
      this.editParticipantForm.markAllAsTouched();
      return;
    }

    this.showSpinner = true;
    const participantEditData: Record<string, any> = {};

    if (formData) {
      Object.keys(formData).forEach(key => {
        if (formData[key] !== "" && formData[key] !== null) {
          if (key === "selectedRole") {
            participantEditData['role'] = formData[key];
          } else {
            participantEditData[key] = formData[key];
          }
        }
      });
    }
    participantEditData['userId'] = this.participantData.id;

    this._requestsService.editParticipant(participantEditData).subscribe({
      next: (response) => {
        this.showSpinner = false;
        this.isAddParticipantSuccessful = true;
        this.participantData = {...this.participantData, ...participantEditData};
      },
      error: (error) => {
        this.isDuplicateUsername = error.error.username.status_code = 403 ? true : false;
        this.showSpinner = false;
      }
    }
    );
  }

  deleteConfirmation(event: Event) {
    this._confirmationService.confirm({
        target: event.target as EventTarget,
        message: 'Do you want to delete this participant?',
        header: 'Delete Confirmation',
        icon: 'pi pi-info-circle',
        acceptButtonStyleClass:"p-button-danger p-button-text",
        rejectButtonStyleClass:"p-button-text p-button-text",
        acceptIcon:"none",
        rejectIcon:"none",

        accept: () => {
          const participantData = {
            'userId': this.participantData.id,
            'active': false
          };
          this._requestsService.editParticipant(participantData).subscribe({
            next: (response) => {
              this.isAddParticipantSuccessful = true;
              this.showParticipantSummaryDialog = false;
            },
            error: (error) => {}
          })

        },
        reject: () => {}
    });
  }

  onDialogHide(): void {
    if (this.isAddParticipantSuccessful){
      this.getUsers();
    }
    this.selectedRows = [];
    this.username = '';
    this.showSpinner = false;
    this.isAddParticipantSuccessful = false;
    this.isDuplicateUsername = false;
    this.deviceSummary = {};
    this.defaultVisualizationOption = 'all_time';

    if (this.usernameInput) {
      this.usernameInput.control.markAsPristine(); // Reset ngModel state on dialog show
      this.usernameInput.control.markAsUntouched();
    }
    this.participantForm.reset();
    this.editParticipantForm.reset();
  }

  onSelectParticipantLegacy(participant: any) {
    this.showParticipantSummaryDialog = true;
    this.currentParticipant = participant;
    console.log(participant);

    this._router.navigate(
      ['/dashboard/participant-summary'],
      {
        state:{
          username: participant.data.username,
          createdAt: participant.data.created_at
        }
      }
    );
  }

  onSelectParticipant(participant: any) {
    this.showParticipantSummaryDialog = true;
    this.currentParticipant = participant;
    this.participantData = participant.data;
    this.participantData.devicesLoaded = false;

    this._requestsService.getDevicesByUsername(this.participantData.username).subscribe({
      next: (response) => {
        this.participantData.devicesLoaded = true;
        this.participantData.devices = response.devices;
        this.deviceDetailsVisible = new Array(this.participantData.devices.length).fill(false);
      }

    })
  }

  toggleDeviceDetails(event: Event, index: number): void {
    event.stopPropagation();
    this.deviceDetailsVisible[index] = !this.deviceDetailsVisible[index];
  }

  //TODO: Rename this function
  showDeviceTable(index: number): void {
    this.showDeviceTableDialog = true;

    const username = this.participantData.username;
    const device_type: 'scale' = this.participantData.devices[index].device_type;
    const deviceSummaryName = this.icons[device_type].summaryName!;
    this.deviceName = this.icons[device_type].prettyName;
    this.participantData.deviceSummaryLoaded = false;

    this._requestsService.getDeviceSummaryByUsername(username, device_type).subscribe({
      next: (response) => {
          this.setDeviceSummaryData(response[deviceSummaryName], device_type)
          return;
        }
      }
    );
  }

  setDeviceSummaryData(deviceSummary: any, deviceType: DeviceType): void {
    if (deviceSummary.length == 0) {
      this.deviceSummary = {
        data:    [],
      };
      this.participantData.deviceSummaryLoaded = true;
      return;
    }

    this.deviceSummary = {
      data:       deviceSummary,
      deviceType: deviceType,
      columns:    Object.keys(deviceSummary[0]),
      dataFields: this.chartFields[deviceType],
      chartData: {
        labels: deviceSummary.map((item: { date: string | number | Date; }) => new Date(item.date).toLocaleDateString()).reverse(),
        datasets: []
      },
    };

    for (let i = 0; i < this.deviceSummary.dataFields.length; i++) {
      const color = this._uiUtilsService.getRandomColor();
      const currentField: DeviceType = this.deviceSummary.dataFields[i].fieldName;
      const deviceType: DeviceType = this.deviceSummary.deviceType;

      this.deviceSummary.dataFields[i].color = color;

      const datasetValue = {
        field: currentField,
        label: this.chartFields[deviceType][i].label,
        data: this.deviceSummary.data.map((item: any) => item[currentField])
                .reverse()
                .map((value: any) => value === null ? this.nullReplaceValue : value),
        fill: true,
        borderColor: color,
        backgroundColor: this._uiUtilsService.getColorWithTransparency(color, 0.5),
        hidden: true,
        tension: 0.5
      };
      this.deviceSummary.chartData.datasets.push(datasetValue);

    }

    this.selectedColumns = this.deviceSummary.dataFields
    this.calculateMaxColumnWidth();

    this.deviceSummary.filteredChartData = this.deviceSummary.chartData;
    this.deviceSummary.chartData.datasets[0].hidden = false;
    this.deviceSummary.dataFields[0].hidden = false;
    this.deviceSummary.chartOptions = this._uiUtilsService.getLineChartOptions();
    this.deviceSummary.chartOptions.plugins.legend.onClick = this.chartLegendClick.bind(this);

    this.participantData.deviceSummaryLoaded = true;

  }

  onDeviceFieldSelected(selectedField: DeviceField): void {
    const ci = this.chart.chart;
    const indexOfInstance= ci._metasets.findIndex(
      (meta: any) => meta.label === selectedField.label
    )

    if (indexOfInstance == -1) {
      return;
    }

    if (ci.isDatasetVisible(indexOfInstance)) {
        ci.hide(indexOfInstance);
    } else {
        ci.show(indexOfInstance);
    }
  }

  chartLegendClick(event: any, legendItem: any, legend: any): void {
    const indexOfField = this.deviceSummary.dataFields.findIndex(
      (field: any) => field.label === legendItem.text
    )

    const index = legendItem.datasetIndex;
    const ci = legend.chart;
    if (ci.isDatasetVisible(index)) {
        ci.hide(index);
        legendItem.hidden = true;
    } else {
        ci.show(index);
        legendItem.hidden = false;
    }
    if (indexOfField != -1) {
      this.deviceSummary.dataFields[indexOfField].hidden = legendItem.hidden;
      this._changeDetectorRef.detectChanges();
    }
  }

  onChartDateOptionClick(event: any) {
    const now = new Date();
    let startDate: Date;

    switch (this.defaultVisualizationOption) {
      case 'last_week':
        startDate = new Date(now.setDate(now.getDate() - 7));
        break;
      case 'last_month':
        startDate = new Date(now.setMonth(now.getMonth() - 1));
        break;
      case 'last_3_months':
        startDate = new Date(now.setMonth(now.getMonth() - 3));
        break;
      case 'last_year':
        startDate = new Date(now.setFullYear(now.getFullYear() - 1));
        break;
      case 'all_time':
      default:
        startDate = new Date(0); // A date in the far past
        break;
    }

    //TODO: Try to copy data without using JSON parse, as it may cause performance issues
    const filteredData = JSON.parse(JSON.stringify(this.deviceSummary.chartData));;

    filteredData.labels = this.deviceSummary.chartData.labels.filter(
      (label: any) => new Date(label) >= startDate)
    ;

    filteredData.datasets.forEach((dataset: any, index: number) => {
      dataset.data = this.deviceSummary.chartData.datasets[index].data.slice(
        this.deviceSummary.chartData.labels.findIndex(
          (label: any) => new Date(label) >= startDate
        )
      );
      dataset.hidden = this.deviceSummary.dataFields[index].hidden;
    });

    this.deviceSummary.filteredChartData = filteredData;

    if (this.defaultDataVisualizationOption === 'graph') {
      this.chart.chart.update();
    }
  }

  downloadCSV() {
    const fileName = this.participantData.username + '-' + this.deviceSummary.deviceType + '-device-summary.csv';
    this._csvService.downloadCSV(this.deviceSummary, fileName);
  }

  onSelectedColumnsChange(event: any) {
    this.calculateMaxColumnWidth();
  }

  closeParticipants() {
    //Go to /dashboard
    this._router.navigate(['/dashboard']);
  }

}
