estrutura_bd = """
create or replace view duty_view as
  select 
    a.id as id,
    a.code as code,

    a.type_id as type_id,
    b.code as type_code,
    b.name as type_name,
    b.tags as type_tags,

    a.situation_id as situation_id,
    c.code as situation_code,
    c.name as situation_name,
    c.needs_coverage as situation_needs_coverage,
    c.tags as situation_tags,

    a.shift as shift,
    a.activity_type as activity_type,

    a.partner_id as partner_id,
    d.code as partner_code,
    d.name as partner_name,
    d.tax_id as partner_tax_id,
    d.crm_code as partner_crm_code,
    d.cns_code as partner_cns_code,
    d.tags as partner_tags,

    a.local_id as local_id,
    e.code as local_code,
    e.name as local_name,
    e.type as local_type,
    e.region as local_region,
    e.address_name as local_address_name,
    e.address_zip_code as local_address_zip_code,
    e.address_line1 as local_address_line1,
    e.address_line2 as local_address_line2,
    e.address_line3 as local_address_line3,
    e.address_region as local_address_region,
    e.address_city as local_address_city,
    e.address_state as local_address_state,
    e.tags as local_tags,

    a.sector_id as sector_id,
    f.name as sector_name,
    f.active as sector_active,

    a.contract_id as contract_id,
    g.code as contract_code,
    g.name as contract_name,
    g.number as contract_number,
    g.start_date as contract_start_date,
    g.end_date as contract_end_date,
    g.tags as contract_tags,
    
    a.starts_at as starts_at,
    a.ends_at as ends_at,
    a.duration_in_minutes as duration_in_minutes,
    a.checked_in_at as checked_in_at,
    a.checked_out_at as checked_out_at,
    a.realized_in_minutes as realized_in_minutes,
    a.amount as amount,

    a.doctor_id as doctor_id,
    h.code as doctor_code,
    h.name as doctor_name,
    h.tax_id as doctor_tax_id,
    h.crm_code as doctor_crm_code,
    h.cns_code as doctor_cns_code,
    h.tags as doctor_tags,

    a.permanent_doctor_id as permanent_doctor_id,
    i.code as permanent_doctor_code,
    i.name as permanent_doctor_name,
    i.tax_id as permanent_doctor_tax_id,
    i.crm_code as permanent_doctor_crm_code,
    i.cns_code as permanent_doctor_cns_code,
    i.tags as permanent_doctor_tags,

    a.doctor_notes as doctor_notes,
    a.internal_notes as internal_notes,
    a.status as status,
    a.should_pay_anyways as should_pay_anyways,
    a.should_pay_reason as should_pay_reason,
    a.doctor_paid_at as doctor_paid_at,
    a.doctor_was_paid as doctor_was_paid,
    a.advance_amount as advance_amount,
    a.cost_amount as cost_amount,
    a.charge_amount as charge_amount,
    a.external_ref as external_ref,
    a.tags as tags,

    a.created_id as created_id,
    j.full_name as created_full_name,
    a.created_at as created_at,
    a.updated_id as updated_id,
    k.full_name as updated_full_name,
    a.updated_at as updated_at

    from "duty" a
      left join "duty_type" b on a.type_id = b.id
      left join "duty_situation" c on a.situation_id = c.id
      left join "partner" d on a.partner_id = d.id
      left join "local" e on a.local_id = e.id
      left join "local_sector" f on a.sector_id = f.id
      left join "contract" g on a.contract_id = g.id
      left join "partner" h on a.doctor_id = h.id
      left join "partner" i on a.permanent_doctor_id = i.id
      left join "user" j on a.created_id = j.id
      left join "user" k on a.updated_id = k.id;
"""
