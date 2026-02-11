<template>
  <div>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" location="top">
      {{ snackbar.text }}
    </v-snackbar>
    <v-app-bar color="primary" density="compact" class="px-4 py-2">
      <v-app-bar-title class="pl-2">Панель администратора</v-app-bar-title>
      <v-spacer />
      <span class="mr-2">{{ userStore.user?.username }}</span>
      <v-btn variant="text" icon="mdi-logout" @click="logout" />
    </v-app-bar>

    <v-main class="pa-50">
      <v-container fluid class="pa-0 pa-sm-4">
        <v-tabs v-model="activeTab" class="mb-4">
          <v-tab value="prices">Цены на макулатуру</v-tab>
          <v-tab value="news">Новости</v-tab>
          <v-tab value="companies">Компании</v-tab>
          <v-tab value="institutions">Организации</v-tab>
          <v-tab value="requests">Заявки</v-tab>
        </v-tabs>

        <v-window v-model="activeTab">
          <!-- Prices -->
          <v-window-item value="prices">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Справочник цен (руб/кг)
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openPriceDialog()">
                  Добавить цену
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="priceHeaders"
                :items="prices"
                :loading="loadingPrices"
                item-value="id"
              >
                <template #item.material_type_display="{ item }">
                  {{ item.material_type_display || item.material_type }}
                </template>
                <template #item.price_per_kg="{ item }">
                  {{ item.price_per_kg }} руб/кг
                </template>
                <template #item.valid_to="{ item }">
                  {{ item.valid_to || '—' }}
                </template>
                <template #item.is_active="{ item }">
                  <v-chip :color="item.is_active ? 'success' : 'default'" size="small">
                    {{ item.is_active ? 'Да' : 'Нет' }}
                  </v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openPriceDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeletePrice(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="priceDialog" max-width="500" persistent>
              <v-card>
                <v-card-title>{{ editingPrice ? 'Редактировать цену' : 'Новая цена' }}</v-card-title>
                <v-card-text>
                  <v-select
                    v-model="priceForm.material_type"
                    :items="materialTypeItems"
                    label="Тип макулатуры"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-text-field
                    v-model="priceForm.price_per_kg"
                    label="Цена за кг (руб)"
                    type="number"
                    min="0"
                    step="0.01"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-text-field
                    v-model="priceForm.valid_from"
                    label="Действует с (дата)"
                    type="date"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-text-field
                    v-model="priceForm.valid_to"
                    label="Действует по (дата, необяз.)"
                    type="date"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-checkbox v-model="priceForm.is_active" label="Активна" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="priceDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingPrice" @click="savePrice">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deletePriceDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить запись о цене?</v-card-title>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deletePriceDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingPrice" @click="doDeletePrice">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- News -->
          <v-window-item value="news">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Новости
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openNewsDialog()">
                  Добавить новость
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="newsHeaders"
                :items="newsArticles"
                :loading="loadingNews"
                item-value="id"
              >
                <template #item.is_published="{ item }">
                  <v-switch
                    :model-value="item.is_published"
                    hide-details
                    density="compact"
                    color="success"
                    @update:model-value="toggleNewsPublish(item)"
                  />
                </template>
                <template #item.created_at="{ item }">
                  {{ formatNewsDate(item.created_at) }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openNewsDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteNews(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="newsDialog" max-width="640" persistent scrollable>
              <v-card>
                <v-card-title>{{ editingNews ? 'Редактировать новость' : 'Новая новость' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-text-field
                    v-model="newsForm.title"
                    label="Заголовок *"
                    variant="outlined"
                    class="mb-3"
                  />
                  <v-textarea
                    v-model="newsForm.content"
                    label="Содержание *"
                    variant="outlined"
                    rows="6"
                    class="mb-3"
                  />
                  <v-file-input
                    v-model="newsForm.imageFile"
                    label="Изображение (необяз.)"
                    accept="image/*"
                    prepend-icon=""
                    prepend-inner-icon="mdi-camera"
                    variant="outlined"
                    class="mb-3"
                    @update:model-value="onNewsImageChange"
                  />
                  <v-img
                    v-if="newsForm.imagePreview"
                    :src="newsForm.imagePreview"
                    max-height="200"
                    cover
                    class="rounded mb-3"
                  />
                  <v-checkbox v-model="newsForm.is_published" label="Опубликовано" />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="newsDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingNews" @click="saveNews">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deleteNewsDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить новость?</v-card-title>
                <v-card-text>
                  Будет удалена новость «{{ newsToDelete?.title }}». Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteNewsDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingNews" @click="doDeleteNews">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Companies -->
          <v-window-item value="companies">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center">
                Все компании
                <v-spacer />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openCompanyDialog()">
                  Добавить компанию
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="companyHeaders"
                :items="companies"
                :loading="loadingCompanies"
                item-value="id"
              >
                <template #item.contact_phone="{ item }">
                  {{ item.contact_phone }} / {{ item.contact_email }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openCompanyCard(item)">Просмотр</v-btn>
                  <v-btn size="small" variant="text" @click="openCompanyDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteCompany(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="companyCardDialog" max-width="640" persistent>
              <v-card v-if="companyCard">
                <v-card-title class="d-flex align-center">
                  Карточка компании
                  <v-spacer />
                  <v-btn icon variant="text" @click="companyCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2">
                  <p><strong>Название:</strong> {{ companyCard.company_name }}</p>
                  <p><strong>Почта:</strong> {{ companyCard.contact_email }}</p>
                  <p><strong>Телефон:</strong> {{ companyCard.contact_phone }}</p>
                  <p><strong>Адрес:</strong> {{ companyCard.address || '—' }}</p>
                  <p><strong>Юр. адрес:</strong> {{ companyCard.legal_address || '—' }}</p>
                  <p><strong>ИНН:</strong> {{ companyCard.inn || '—' }}</p>
                  <p><strong>КПП:</strong> {{ companyCard.kpp || '—' }}</p>
                  <p><strong>ОГРН:</strong> {{ companyCard.ogrn || '—' }}</p>
                  <p><strong>Р/с:</strong> {{ companyCard.bank_account || '—' }}</p>
                  <p><strong>Банк:</strong> {{ companyCard.bank_name || '—' }}</p>
                  <p><strong>БИК:</strong> {{ companyCard.bik || '—' }}</p>
                  <p><strong>Корр. счёт:</strong> {{ companyCard.corr_account || '—' }}</p>
                  <p><strong>Сайт:</strong> {{ companyCard.website || '—' }}</p>
                  <p v-if="companyCard.description"><strong>Описание:</strong><br />{{ companyCard.description }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="companyCardDialog = false; openCompanyDialog(companyCard)">Изменить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="companyDialog" max-width="600" persistent scrollable>
              <v-card>
                <v-card-title>{{ editingCompany ? 'Редактировать компанию' : 'Новая компания' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-alert v-if="Object.keys(companyFormErrors).length" type="error" density="compact" class="mb-2">
                    <div v-for="(msgs, key) in companyFormErrors" :key="key">
                      {{ Array.isArray(msgs) ? msgs.join(' ') : msgs }}
                    </div>
                  </v-alert>
                  <v-text-field
                    v-model="companyForm.company_name"
                    label="Название компании *"
                    variant="outlined"
                    class="mb-2"
                    :error-messages="companyFormErrors.company_name"
                  />
                  <v-text-field
                    v-model="companyForm.contact_email"
                    label="Почта *"
                    type="email"
                    variant="outlined"
                    class="mb-2"
                    :disabled="!!editingCompany"
                    :error-messages="companyFormErrors.contact_email || companyFormErrors.email"
                  />
                  <v-text-field
                    v-model="companyForm.password"
                    :label="editingCompany ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль (необяз. — сгенерируется)'"
                    type="password"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.contact_phone"
                    label="Телефон *"
                    variant="outlined"
                    class="mb-2"
                    hint="Формат: 7 XXX XXX XX XX или +7 XXX XXX XX XX (плюс необязателен)"
                    persistent-hint
                    :error-messages="companyFormErrors.contact_phone"
                  />
                  <v-textarea
                    v-model="companyForm.address"
                    label="Адрес *"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="companyForm.legal_address"
                    label="Юридический адрес (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.inn"
                    label="ИНН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.kpp"
                    label="КПП (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.ogrn"
                    label="ОГРН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bank_account"
                    label="Расчётный счёт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bank_name"
                    label="Название банка (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.bik"
                    label="БИК (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.corr_account"
                    label="Корр. счёт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="companyForm.website"
                    label="Сайт (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="companyForm.description"
                    label="Описание (необяз.)"
                    variant="outlined"
                    rows="2"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="companyDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingCompany" @click="saveCompany">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deleteCompanyDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить компанию?</v-card-title>
                <v-card-text>
                  Будет удалена компания «{{ companyToDelete?.company_name }}» и все связанные организации. Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteCompanyDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingCompany" @click="doDeleteCompany">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Institutions -->
          <v-window-item value="institutions">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap">
                Все организации
                <v-spacer />
                <v-text-field
                  v-model="institutionSearchName"
                  density="compact"
                  hide-details
                  label="Поиск по названию"
                  variant="outlined"
                  clearable
                  style="max-width: 220px"
                  class="mr-2"
                />
                <v-btn color="primary" prepend-icon="mdi-plus" @click="openInstitutionDialog()">
                  Добавить организацию
                </v-btn>
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="institutionHeaders"
                :items="filteredInstitutions"
                :loading="loadingInstitutions"
                item-value="id"
              >
                <template #item.contacts="{ item }">
                  {{ item.contact_person }} / {{ item.phone }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openInstitutionCard(item)">Просмотр</v-btn>
                  <v-btn size="small" variant="text" @click="openInstitutionDialog(item)">Изменить</v-btn>
                  <v-btn size="small" variant="text" color="error" @click="confirmDeleteInstitution(item)">Удалить</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="institutionCardDialog" max-width="640" persistent>
              <v-card v-if="institutionCard">
                <v-card-title class="d-flex align-center">
                  Карточка организации
                  <v-spacer />
                  <v-btn icon variant="text" @click="institutionCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2">
                  <p><strong>Название:</strong> {{ institutionCard.institution_name }}</p>
                  <p><strong>Компания:</strong> {{ institutionCard.parent_company_name }}</p>
                  <p><strong>Тип:</strong> {{ institutionCard.institution_type }}</p>
                  <p><strong>Почта / Логин:</strong> {{ institutionCard.email }}</p>
                  <p><strong>Контактное лицо:</strong> {{ institutionCard.contact_person }}</p>
                  <p><strong>Телефон:</strong> {{ institutionCard.phone }}</p>
                  <p><strong>Адрес:</strong> {{ institutionCard.address || '—' }}</p>
                  <p><strong>Юр. адрес:</strong> {{ institutionCard.legal_address || '—' }}</p>
                  <p><strong>ИНН:</strong> {{ institutionCard.inn || '—' }}</p>
                  <p><strong>КПП:</strong> {{ institutionCard.kpp || '—' }}</p>
                  <p><strong>Контакт на площадке:</strong> {{ institutionCard.contact_person_on_site || '—' }}</p>
                  <p><strong>Телефон на площадке:</strong> {{ institutionCard.phone_on_site || '—' }}</p>
                  <p><strong>Предпочтительные дни:</strong> {{ institutionCard.preferred_days || '—' }}</p>
                  <p><strong>Предпочтительные часы:</strong> {{ institutionCard.preferred_hours || '—' }}</p>
                  <p v-if="institutionCard.access_details"><strong>Детали доступа:</strong><br />{{ institutionCard.access_details }}</p>
                  <p v-if="institutionCard.container_location"><strong>Расположение контейнера:</strong><br />{{ institutionCard.container_location }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="institutionCardDialog = false; openInstitutionDialog(institutionCard)">Изменить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="institutionDialog" max-width="600" persistent scrollable>
              <v-card>
                <v-card-title>{{ editingInstitution ? 'Редактировать организацию' : 'Новая организация' }}</v-card-title>
                <v-card-text style="max-height: 70vh" class="overflow-y-auto">
                  <v-alert v-if="Object.keys(institutionFormErrors).length" type="error" density="compact" class="mb-2">
                    <div v-for="(msgs, key) in institutionFormErrors" :key="key">
                      {{ Array.isArray(msgs) ? msgs.join(' ') : msgs }}
                    </div>
                  </v-alert>
                  <v-select
                    v-model="institutionForm.parent_company"
                    :items="companies"
                    item-title="company_name"
                    item-value="id"
                    label="Компания (заявки идут только в эту компанию) *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.email"
                    label="Почта / Логин (для входа) *"
                    type="email"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.password"
                    :label="editingInstitution ? 'Новый пароль (оставьте пустым, чтобы не менять)' : 'Пароль (необяз. — сгенерируется)'"
                    type="password"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.institution_name"
                    label="Название учреждения *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.institution_type"
                    label="Тип организации *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.address"
                    label="Адрес *"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.contact_person"
                    label="Контактное лицо *"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.phone"
                    label="Телефон *"
                    variant="outlined"
                    hint="Формат: 7 XXX XXX XX XX или +7 XXX XXX XX XX (плюс необязателен)"
                    persistent-hint
                    class="mb-2"
                    :error-messages="institutionFormErrors.phone"
                  />
                  <v-textarea
                    v-model="institutionForm.legal_address"
                    label="Юридический адрес (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.inn"
                    label="ИНН (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.kpp"
                    label="КПП (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.contact_person_on_site"
                    label="Контакт на площадке (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.phone_on_site"
                    label="Телефон на площадке (необяз.)"
                    variant="outlined"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.preferred_days"
                    label="Предпочтительные дни (необяз.)"
                    variant="outlined"
                    placeholder="пн, ср, пт"
                    class="mb-2"
                  />
                  <v-text-field
                    v-model="institutionForm.preferred_hours"
                    label="Предпочтительные часы (необяз.)"
                    variant="outlined"
                    placeholder="09:00-18:00"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.access_details"
                    label="Детали доступа (необяз.)"
                    variant="outlined"
                    rows="2"
                    class="mb-2"
                  />
                  <v-textarea
                    v-model="institutionForm.container_location"
                    label="Расположение контейнера (необяз.)"
                    variant="outlined"
                    rows="2"
                  />
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="institutionDialog = false">Отмена</v-btn>
                  <v-btn color="primary" :loading="savingInstitution" @click="saveInstitution">Сохранить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>

            <v-dialog v-model="deleteInstitutionDialog" max-width="400" persistent>
              <v-card>
                <v-card-title>Удалить организацию?</v-card-title>
                <v-card-text>
                  Будет удалена организация «{{ institutionToDelete?.institution_name }}». Действие нельзя отменить.
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn variant="text" @click="deleteInstitutionDialog = false">Отмена</v-btn>
                  <v-btn color="error" :loading="deletingInstitution" @click="doDeleteInstitution">Удалить</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>

          <!-- Requests -->
          <v-window-item value="requests">
            <v-card class="rounded-lg" elevation="1">
              <v-card-title class="d-flex align-center flex-wrap ga-2">
                Все заявки
                <v-select
                  v-model="requestStatusFilter"
                  :items="requestStatusOptions"
                  density="compact"
                  hide-details
                  label="Статус"
                  variant="outlined"
                  style="max-width: 140px"
                />
                <v-text-field
                  v-model="requestInstitutionFilter"
                  density="compact"
                  hide-details
                  label="Организация"
                  variant="outlined"
                  clearable
                  style="max-width: 200px"
                />
                <v-text-field
                  v-model="requestCompanyFilter"
                  density="compact"
                  hide-details
                  label="Компания"
                  variant="outlined"
                  clearable
                  style="max-width: 200px"
                />
                <v-spacer />
              </v-card-title>
              <v-divider />
              <v-data-table
                :headers="requestHeaders"
                :items="filteredAdminRequests"
                :loading="loadingRequests"
                item-value="id"
              >
                <template #item.request_number="{ item }">
                  {{ item.request_number || item.id }}
                </template>
                <template #item.status="{ item }">
                  <v-chip :color="requestStatusColor(item.status)" size="small">
                    {{ requestStatusLabel(item.status) }}
                  </v-chip>
                </template>
                <template #item.estimated_value="{ item }">
                  {{ item.estimated_value != null ? `${item.estimated_value} руб.` : '—' }}
                </template>
                <template #item.actual_value="{ item }">
                  {{ item.actual_value != null ? `${item.actual_value} руб.` : '—' }}
                </template>
                <template #item.actions="{ item }">
                  <v-btn size="small" variant="text" @click="openRequestCard(item)">Просмотр</v-btn>
                </template>
              </v-data-table>
            </v-card>

            <v-dialog v-model="requestCardDialog" max-width="640" persistent>
              <v-card v-if="requestCard">
                <v-card-title class="d-flex align-center">
                  Заявка {{ requestCard.request_number || requestCard.id }}
                  <v-spacer />
                  <v-btn icon variant="text" @click="requestCardDialog = false">×</v-btn>
                </v-card-title>
                <v-divider />
                <v-card-text class="text-body-2">
                  <p><strong>Организация:</strong> {{ requestCard.institution_name }}</p>
                  <p><strong>Компания:</strong> {{ requestCard.receiving_company_name }}</p>
                  <p><strong>Статус:</strong> {{ requestStatusLabel(requestCard.status) }}</p>
                  <p><strong>Тип макулатуры:</strong> {{ requestCard.material_type_display || requestCard.material_type || '—' }}</p>
                  <p><strong>Вес (кг):</strong> {{ requestCard.estimated_amount ?? requestCard.paper_weight_kg ?? '—' }}</p>
                  <p><strong>Ориент. стоимость:</strong> {{ requestCard.estimated_value != null ? `${requestCard.estimated_value} руб.` : '—' }}</p>
                  <p><strong>Факт. стоимость:</strong> {{ requestCard.actual_value != null ? `${requestCard.actual_value} руб.` : '—' }}</p>
                  <p><strong>Желаемая дата:</strong> {{ requestCard.desired_date || '—' }}</p>
                  <p><strong>Комментарий:</strong> {{ requestCard.comment || '—' }}</p>
                  <p><strong>Дата создания:</strong> {{ requestCard.created_at }}</p>
                </v-card-text>
                <v-card-actions>
                  <v-spacer />
                  <v-btn color="primary" @click="requestCardDialog = false">Закрыть</v-btn>
                </v-card-actions>
              </v-card>
            </v-dialog>
          </v-window-item>
        </v-window>
      </v-container>
    </v-main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api/axios'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/user'
import type { CompanyProfile, InstitutionProfile, CollectionRequest, NewsArticle, PriceList } from '@/types'

const router = useRouter()
const authStore = useAuthStore()
const userStore = useUserStore()

const activeTab = ref('prices')
const prices = ref<PriceList[]>([])
const companies = ref<CompanyProfile[]>([])
const institutions = ref<InstitutionProfile[]>([])
const adminRequests = ref<CollectionRequest[]>([])
const loadingPrices = ref(false)
const loadingCompanies = ref(false)
const loadingInstitutions = ref(false)
const loadingRequests = ref(false)
const priceDialog = ref(false)
const editingPrice = ref<PriceList | null>(null)
const savingPrice = ref(false)
const priceForm = reactive({
  material_type: 'paper',
  price_per_kg: '',
  valid_from: '',
  valid_to: '' as string,
  is_active: true,
})
const deletePriceDialog = ref(false)
const priceToDelete = ref<PriceList | null>(null)
const deletingPrice = ref(false)
const requestStatusFilter = ref('all')

const newsArticles = ref<NewsArticle[]>([])
const loadingNews = ref(false)
const newsDialog = ref(false)
const editingNews = ref<NewsArticle | null>(null)
const savingNews = ref(false)
const newsForm = reactive({
  title: '',
  content: '',
  imageFile: null as File[] | null,
  imagePreview: '' as string,
  is_published: true,
})
const deleteNewsDialog = ref(false)
const newsToDelete = ref<NewsArticle | null>(null)
const deletingNews = ref(false)

const newsHeaders = [
  { title: 'Заголовок', key: 'title' },
  { title: 'Дата', key: 'created_at', width: '140' },
  { title: 'Опубликовано', key: 'is_published', width: '120' },
  { title: 'Автор', key: 'author_username', width: '120' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const companyDialog = ref(false)
const editingCompany = ref<CompanyProfile | null>(null)
const savingCompany = ref(false)
const companyForm = reactive({
  company_name: '',
  contact_email: '',
  password: '',
  contact_phone: '',
  address: '',
  legal_address: '',
  inn: '',
  kpp: '',
  ogrn: '',
  bank_account: '',
  bank_name: '',
  bik: '',
  corr_account: '',
  website: '',
  description: '',
})
const deleteCompanyDialog = ref(false)
const companyToDelete = ref<CompanyProfile | null>(null)
const deletingCompany = ref(false)
const companyCardDialog = ref(false)
const companyCard = ref<CompanyProfile | null>(null)
const companyFormErrors = ref<Record<string, string[]>>({})
const snackbar = ref({ show: false, text: '', color: 'error' })

const institutionDialog = ref(false)
const editingInstitution = ref<InstitutionProfile | null>(null)
const savingInstitution = ref(false)
const institutionForm = reactive({
  parent_company: null as number | null,
  email: '',
  password: '',
  institution_name: '',
  institution_type: '',
  address: '',
  contact_person: '',
  phone: '',
  legal_address: '',
  inn: '',
  kpp: '',
  contact_person_on_site: '',
  phone_on_site: '',
  preferred_days: '',
  preferred_hours: '',
  access_details: '',
  container_location: '',
})
const deleteInstitutionDialog = ref(false)
const institutionToDelete = ref<InstitutionProfile | null>(null)
const deletingInstitution = ref(false)
const institutionFormErrors = ref<Record<string, string[]>>({})

const materialTypeItems = [
  { title: 'Бумага', value: 'paper' },
  { title: 'Картон', value: 'cardboard' },
  { title: 'Газеты', value: 'newspapers' },
  { title: 'Смешанная', value: 'mixed' },
  { title: 'Архивная', value: 'archive' },
]

const priceHeaders = [
  { title: 'Тип макулатуры', key: 'material_type_display' },
  { title: 'Цена', key: 'price_per_kg' },
  { title: 'Действует с', key: 'valid_from' },
  { title: 'Действует по', key: 'valid_to' },
  { title: 'Активна', key: 'is_active' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const companyHeaders = [
  { title: 'Название', key: 'company_name' },
  { title: 'Контакты', key: 'contact_phone' },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const institutionHeaders = [
  { title: 'Название', key: 'institution_name' },
  { title: 'Компания', key: 'parent_company_name' },
  { title: 'Тип', key: 'institution_type' },
  { title: 'Контакты', key: 'contacts' },
  { title: 'Адрес', key: 'address' },
  { title: 'Действия', key: 'actions', sortable: false, width: '180' },
]

const requestHeaders = [
  { title: 'Номер', key: 'request_number', width: '140' },
  { title: 'Организация', key: 'institution_name' },
  { title: 'Компания', key: 'receiving_company_name' },
  { title: 'Тип макулатуры', key: 'material_type_display' },
  { title: 'Вес (кг)', key: 'estimated_amount' },
  { title: 'Ориент. стоимость', key: 'estimated_value' },
  { title: 'Факт. стоимость', key: 'actual_value' },
  { title: 'Статус', key: 'status' },
  { title: 'Дата создания', key: 'created_at' },
  { title: 'Действия', key: 'actions', sortable: false, width: '100' },
]

const requestStatusOptions = [
  { title: 'Все', value: 'all' },
  { title: 'Новые', value: 'new' },
  { title: 'Принятые', value: 'accepted' },
  { title: 'Завершённые', value: 'completed' },
]

const institutionSearchName = ref('')
const requestInstitutionFilter = ref('')
const requestCompanyFilter = ref('')
const institutionCardDialog = ref(false)
const institutionCard = ref<InstitutionProfile | null>(null)
const requestCardDialog = ref(false)
const requestCard = ref<CollectionRequest | null>(null)

const filteredInstitutions = computed(() => {
  const q = institutionSearchName.value?.trim().toLowerCase() || ''
  if (!q) return institutions.value
  return institutions.value.filter((i) => i.institution_name.toLowerCase().includes(q))
})

const filteredAdminRequests = computed(() => {
  let list = adminRequests.value
  if (requestStatusFilter.value !== 'all') {
    list = list.filter((r) => r.status === requestStatusFilter.value)
  }
  const instQ = requestInstitutionFilter.value?.trim().toLowerCase() || ''
  if (instQ) {
    list = list.filter((r) => (r.institution_name || '').toLowerCase().includes(instQ))
  }
  const compQ = requestCompanyFilter.value?.trim().toLowerCase() || ''
  if (compQ) {
    list = list.filter((r) => (r.receiving_company_name || '').toLowerCase().includes(compQ))
  }
  return list
})

function openInstitutionCard(item: InstitutionProfile) {
  institutionCard.value = item
  institutionCardDialog.value = true
}

function openRequestCard(item: CollectionRequest) {
  requestCard.value = item
  requestCardDialog.value = true
}

function requestStatusLabel(s: string) {
  const m: Record<string, string> = { new: 'Новый', accepted: 'Принят', completed: 'Завершён' }
  return m[s] || s
}

function requestStatusColor(s: string) {
  const m: Record<string, string> = { new: 'warning', accepted: 'info', completed: 'success' }
  return m[s] || 'default'
}

async function loadPrices() {
  loadingPrices.value = true
  try {
    const { data } = await api.get<PriceList[]>('/prices/')
    prices.value = data
  } finally {
    loadingPrices.value = false
  }
}

async function loadCompanies() {
  loadingCompanies.value = true
  try {
    const { data } = await api.get<CompanyProfile[]>('/company-profiles/')
    companies.value = data
  } finally {
    loadingCompanies.value = false
  }
}

async function loadInstitutions() {
  loadingInstitutions.value = true
  try {
    const { data } = await api.get<InstitutionProfile[]>('/institutions/')
    institutions.value = data
  } finally {
    loadingInstitutions.value = false
  }
}

async function loadRequests() {
  loadingRequests.value = true
  try {
    const { data } = await api.get<CollectionRequest[]>('/collection-requests/')
    adminRequests.value = data
  } finally {
    loadingRequests.value = false
  }
}

async function loadNews() {
  loadingNews.value = true
  try {
    const { data } = await api.get<NewsArticle[]>('/news/')
    newsArticles.value = Array.isArray(data) ? data : []
  } finally {
    loadingNews.value = false
  }
}

function formatNewsDate(s: string) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function openNewsDialog(item?: NewsArticle) {
  editingNews.value = item ?? null
  if (item) {
    newsForm.title = item.title
    newsForm.content = item.content
    newsForm.is_published = item.is_published
    newsForm.imageFile = null
    newsForm.imagePreview = item.image_url || ''
  } else {
    newsForm.title = ''
    newsForm.content = ''
    newsForm.is_published = true
    newsForm.imageFile = null
    newsForm.imagePreview = ''
  }
  newsDialog.value = true
}

function onNewsImageChange(files: File[] | File | null) {
  const arr = Array.isArray(files) ? files : files ? [files] : []
  if (arr.length > 0) {
    newsForm.imagePreview = URL.createObjectURL(arr[0])
  } else {
    newsForm.imagePreview = ''
  }
}

async function saveNews() {
  savingNews.value = true
  try {
    const formData = new FormData()
    formData.append('title', newsForm.title)
    formData.append('content', newsForm.content)
    formData.append('is_published', String(newsForm.is_published))
    if (newsForm.imageFile && newsForm.imageFile.length > 0) {
      formData.append('image', newsForm.imageFile[0])
    }
    if (editingNews.value) {
      await api.patch(`/news/${editingNews.value.id}/`, formData)
    } else {
      await api.post('/news/', formData)
    }
    newsDialog.value = false
    await loadNews()
  } finally {
    savingNews.value = false
  }
}

function confirmDeleteNews(item: NewsArticle) {
  newsToDelete.value = item
  deleteNewsDialog.value = true
}

async function doDeleteNews() {
  if (!newsToDelete.value) return
  deletingNews.value = true
  try {
    await api.delete(`/news/${newsToDelete.value.id}/`)
    deleteNewsDialog.value = false
    newsToDelete.value = null
    await loadNews()
  } finally {
    deletingNews.value = false
  }
}

async function toggleNewsPublish(item: NewsArticle) {
  try {
    await api.patch(`/news/${item.id}/`, { is_published: !item.is_published })
    await loadNews()
  } catch {
    // ignore
  }
}

function openPriceDialog(item?: PriceList) {
  editingPrice.value = item ?? null
  if (item) {
    priceForm.material_type = item.material_type
    priceForm.price_per_kg = String(item.price_per_kg)
    priceForm.valid_from = item.valid_from
    priceForm.valid_to = item.valid_to || ''
    priceForm.is_active = item.is_active
  } else {
    priceForm.material_type = 'paper'
    priceForm.price_per_kg = ''
    priceForm.valid_from = new Date().toISOString().slice(0, 10)
    priceForm.valid_to = ''
    priceForm.is_active = true
  }
  priceDialog.value = true
}

async function savePrice() {
  savingPrice.value = true
  try {
    const payload = {
      material_type: priceForm.material_type,
      price_per_kg: priceForm.price_per_kg,
      valid_from: priceForm.valid_from,
      valid_to: priceForm.valid_to || null,
      is_active: priceForm.is_active,
    }
    if (editingPrice.value) {
      await api.patch(`/prices/${editingPrice.value.id}/`, payload)
    } else {
      await api.post('/prices/', payload)
    }
    priceDialog.value = false
    await loadPrices()
  } finally {
    savingPrice.value = false
  }
}

function confirmDeletePrice(item: PriceList) {
  priceToDelete.value = item
  deletePriceDialog.value = true
}

async function doDeletePrice() {
  if (!priceToDelete.value) return
  deletingPrice.value = true
  try {
    await api.delete(`/prices/${priceToDelete.value.id}/`)
    deletePriceDialog.value = false
    priceToDelete.value = null
    await loadPrices()
  } finally {
    deletingPrice.value = false
  }
}

function openCompanyCard(item: CompanyProfile) {
  companyCard.value = item
  companyCardDialog.value = true
}

function openCompanyDialog(item?: CompanyProfile) {
  companyFormErrors.value = {}
  editingCompany.value = item ?? null
  if (item) {
    companyForm.company_name = item.company_name
    companyForm.contact_email = item.contact_email
    companyForm.contact_phone = item.contact_phone
    companyForm.address = item.address ?? ''
    companyForm.legal_address = item.legal_address ?? ''
    companyForm.inn = item.inn ?? ''
    companyForm.kpp = item.kpp ?? ''
    companyForm.ogrn = item.ogrn ?? ''
    companyForm.bank_account = item.bank_account ?? ''
    companyForm.bank_name = item.bank_name ?? ''
    companyForm.bik = item.bik ?? ''
    companyForm.corr_account = item.corr_account ?? ''
    companyForm.website = item.website ?? ''
    companyForm.description = item.description ?? ''
  } else {
    companyForm.company_name = ''
    companyForm.contact_email = ''
    companyForm.password = ''
    companyForm.contact_phone = ''
    companyForm.address = ''
    companyForm.legal_address = ''
    companyForm.inn = ''
    companyForm.kpp = ''
    companyForm.ogrn = ''
    companyForm.bank_account = ''
    companyForm.bank_name = ''
    companyForm.bik = ''
    companyForm.corr_account = ''
    companyForm.website = ''
    companyForm.description = ''
  }
  companyDialog.value = true
}

async function saveCompany() {
  companyFormErrors.value = {}
  savingCompany.value = true
  try {
    const payload: Record<string, string> = {
      company_name: companyForm.company_name,
      contact_phone: companyForm.contact_phone,
      address: companyForm.address,
      contact_email: companyForm.contact_email,
      legal_address: companyForm.legal_address || '',
      inn: companyForm.inn || '',
      kpp: companyForm.kpp || '',
      ogrn: companyForm.ogrn || '',
      bank_account: companyForm.bank_account || '',
      bank_name: companyForm.bank_name || '',
      bik: companyForm.bik || '',
      corr_account: companyForm.corr_account || '',
      website: companyForm.website || '',
      description: companyForm.description || '',
    }
    if (editingCompany.value) {
      if (companyForm.password) payload.password = companyForm.password
      await api.patch(`/company-profiles/${editingCompany.value.id}/`, payload)
    } else {
      await api.post('/company-profiles/', {
        ...payload,
        email: companyForm.contact_email,
        password: companyForm.password || undefined,
      })
    }
    companyDialog.value = false
    await loadCompanies()
    snackbar.value = { show: true, text: 'Сохранено', color: 'success' }
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, unknown>; status?: number } }
    const data = ax.response?.data
    if (ax.response?.status === 400 && data && typeof data === 'object') {
      const errors: Record<string, string[]> = {}
      for (const [k, v] of Object.entries(data)) {
        errors[k] = Array.isArray(v) ? v.map(String) : [String(v)]
      }
      companyFormErrors.value = errors
      snackbar.value = { show: true, text: 'Исправьте ошибки в форме', color: 'error' }
    } else {
      snackbar.value = { show: true, text: (data && typeof (data as { detail?: string }).detail === 'string') ? (data as { detail: string }).detail : 'Ошибка при сохранении', color: 'error' }
    }
  } finally {
    savingCompany.value = false
  }
}

function confirmDeleteCompany(item: CompanyProfile) {
  companyToDelete.value = item
  deleteCompanyDialog.value = true
}

async function doDeleteCompany() {
  if (!companyToDelete.value) return
  deletingCompany.value = true
  try {
    await api.delete(`/company-profiles/${companyToDelete.value.id}/`)
    deleteCompanyDialog.value = false
    companyToDelete.value = null
    await loadCompanies()
    await loadInstitutions()
  } finally {
    deletingCompany.value = false
  }
}

async function openInstitutionDialog(item?: InstitutionProfile) {
  institutionFormErrors.value = {}
  editingInstitution.value = item ?? null
  if (item) {
    institutionForm.parent_company = item.parent_company
    institutionForm.email = item.email
    institutionForm.password = ''
    institutionForm.institution_name = item.institution_name
    institutionForm.institution_type = item.institution_type
    institutionForm.address = item.address ?? ''
    institutionForm.contact_person = item.contact_person
    institutionForm.phone = item.phone
    institutionForm.legal_address = item.legal_address ?? ''
    institutionForm.inn = item.inn ?? ''
    institutionForm.kpp = item.kpp ?? ''
    institutionForm.contact_person_on_site = item.contact_person_on_site ?? ''
    institutionForm.phone_on_site = item.phone_on_site ?? ''
    institutionForm.preferred_days = item.preferred_days ?? ''
    institutionForm.preferred_hours = item.preferred_hours ?? ''
    institutionForm.access_details = item.access_details ?? ''
    institutionForm.container_location = item.container_location ?? ''
  } else {
    if (companies.value.length === 0) await loadCompanies()
    institutionForm.parent_company = companies.value.length ? companies.value[0].id : null
    institutionForm.email = ''
    institutionForm.password = ''
    institutionForm.institution_name = ''
    institutionForm.institution_type = ''
    institutionForm.address = ''
    institutionForm.contact_person = ''
    institutionForm.phone = ''
    institutionForm.legal_address = ''
    institutionForm.inn = ''
    institutionForm.kpp = ''
    institutionForm.contact_person_on_site = ''
    institutionForm.phone_on_site = ''
    institutionForm.preferred_days = ''
    institutionForm.preferred_hours = ''
    institutionForm.access_details = ''
    institutionForm.container_location = ''
  }
  institutionDialog.value = true
}

async function saveInstitution() {
  institutionFormErrors.value = {}
  savingInstitution.value = true
  try {
    const payload: Record<string, unknown> = {
      institution_name: institutionForm.institution_name,
      institution_type: institutionForm.institution_type,
      address: institutionForm.address,
      contact_person: institutionForm.contact_person,
      phone: institutionForm.phone,
      email: institutionForm.email,
      legal_address: institutionForm.legal_address || '',
      inn: institutionForm.inn || '',
      kpp: institutionForm.kpp || '',
      contact_person_on_site: institutionForm.contact_person_on_site || '',
      phone_on_site: institutionForm.phone_on_site || '',
      preferred_days: institutionForm.preferred_days || '',
      preferred_hours: institutionForm.preferred_hours || '',
      access_details: institutionForm.access_details || '',
      container_location: institutionForm.container_location || '',
    }
    if (editingInstitution.value) {
      payload.parent_company = institutionForm.parent_company
      if (institutionForm.password) payload.password = institutionForm.password
      await api.patch(`/institutions/${editingInstitution.value.id}/`, payload)
    } else {
      if (institutionForm.parent_company == null) return
      await api.post('/institutions/', {
        ...payload,
        parent_company: institutionForm.parent_company,
        password: institutionForm.password || undefined,
      })
    }
    institutionDialog.value = false
    await loadInstitutions()
    snackbar.value = { show: true, text: 'Сохранено', color: 'success' }
  } catch (err: unknown) {
    const ax = err as { response?: { data?: Record<string, unknown>; status?: number } }
    const data = ax.response?.data
    if (ax.response?.status === 400 && data && typeof data === 'object') {
      const errors: Record<string, string[]> = {}
      for (const [k, v] of Object.entries(data)) {
        errors[k] = Array.isArray(v) ? v.map(String) : [String(v)]
      }
      institutionFormErrors.value = errors
      snackbar.value = { show: true, text: 'Исправьте ошибки в форме', color: 'error' }
    } else {
      snackbar.value = { show: true, text: (data && typeof (data as { detail?: string }).detail === 'string') ? (data as { detail: string }).detail : 'Ошибка при сохранении', color: 'error' }
    }
  } finally {
    savingInstitution.value = false
  }
}

function confirmDeleteInstitution(item: InstitutionProfile) {
  institutionToDelete.value = item
  deleteInstitutionDialog.value = true
}

async function doDeleteInstitution() {
  if (!institutionToDelete.value) return
  deletingInstitution.value = true
  try {
    await api.delete(`/institutions/${institutionToDelete.value.id}/`)
    deleteInstitutionDialog.value = false
    institutionToDelete.value = null
    await loadInstitutions()
  } finally {
    deletingInstitution.value = false
  }
}

function logout() {
  authStore.logout()
  userStore.clearUser()
  router.push({ name: 'Login' })
}

watch(activeTab, (tab) => {
  if (tab === 'prices') loadPrices()
  if (tab === 'news') loadNews()
  if (tab === 'companies') loadCompanies()
  if (tab === 'institutions') loadInstitutions()
  if (tab === 'requests') loadRequests()
})

onMounted(() => {
  loadPrices()
})
</script>
