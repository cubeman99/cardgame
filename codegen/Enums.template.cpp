#include "Enums.h"
#include <algorithm>
#include <map>

namespace enums {

{enums_begin}
template <> std::string EnumName<{enum_name}>()
{
	return "{enum_name}";
}
{enums_end}


{enums_begin}const std::string EnumMap<{enum_name}>::ENUM_NAME = "{enum_name}";

const std::map<{enum_name}, std::string> EnumMap<{enum_name}>::VALUE_TO_STRING =
{
{items_begin}	{{enum_name}::{item_name}, {name_padding}"{item_name}"},
{items_end}};
const std::map<std::string, {enum_name}> EnumMap<{enum_name}>::STRING_TO_VALUE =
{
{items_begin}	{"{item_name}", {name_padding}{enum_name}::{item_name}},
{items_end}};
const std::map<std::string, int> EnumMap<{enum_name}>::STRING_TO_INT =
{
{items_begin}	{"{item_name}", {name_padding}{item_value}},
{items_end}};

{enums_end}
Type GetTagType(GameTag tag)
{
	switch (tag)
	{
	case GameTag::TRIBE:              return Type::ENUM;
	case GameTag::CARD_TYPE:          return Type::ENUM;
	case GameTag::CONTROLLER:         return Type::PLAYER;
	case GameTag::NAME:               return Type::STRING;
	case GameTag::TEXT:               return Type::STRING;
	case GameTag::STEP:               return Type::ENUM;
	case GameTag::CARD_ID:            return Type::STRING;
	case GameTag::ZONE:               return Type::ENUM;
	case GameTag::DECLARED_ATTACK:    return Type::ENTITY;
	case GameTag::DECLARED_INTERCEPT: return Type::ENTITY;
	default: return Type::NUMBER;
	}
}

std::string GetTagEnumValueName(GameTag tag, int value)
{
	switch (tag)
	{
	case GameTag::TRIBE:              return ValueName(Tribe(value));
	case GameTag::CARD_TYPE:          return ValueName(CardType(value));
	case GameTag::STEP:               return ValueName(Step(value));
	case GameTag::ZONE:               return ValueName(Zone(value));
	default: return "UNKNOWN";
	}
}


{enums_begin}
const TypeInfo<{enum_name}> TYPE_INFO_{enum_name:upper} = TypeInfo<{enum_name}>(
	"{enum_name}",
	{
{items_begin}		{"{item_name}", {value_padding}{item_value}},
{items_end}	},{
{items_begin}		{{item_value}, {value_padding}"{item_name}"},
{items_end}	}
);
{enums_end}


const TypeInfoBase* GetTagTypeInfo(GameTag tag)
{
	switch (tag)
	{
	case GameTag::TRIBE:     return &TYPE_INFO_TRIBE;
	case GameTag::CARD_TYPE: return &TYPE_INFO_CARD_TYPE;
	case GameTag::STEP:      return &TYPE_INFO_STEP;
	case GameTag::ZONE:      return &TYPE_INFO_ZONE;
	default: return nullptr;
	}
}

}; // namespace enums
