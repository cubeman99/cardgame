#ifndef _ENUMS_H_
#define _ENUMS_H_

#include <string>
#include <map>


namespace enums {

{enums_begin}
enum class {enum_name}
{
{items_begin}	{item_name}{name_padding} = {item_value},
{items_end}};
{enums_end}

template <typename T_Enum>
class EnumMap
{
public:
	static const std::string ENUM_NAME;
	static const std::map<T_Enum, std::string> VALUE_TO_STRING;
	static const std::map<std::string, T_Enum> STRING_TO_VALUE;
	static const std::map<std::string, int> STRING_TO_INT;
};

template <typename T_Enum>
const std::string EnumMap<T_Enum>::ENUM_NAME = "UNKNOWN";
template <typename T_Enum>
const std::map<T_Enum, std::string> EnumMap<T_Enum>::VALUE_TO_STRING = {};
template <typename T_Enum>
const std::map<std::string, T_Enum> EnumMap<T_Enum>::STRING_TO_VALUE = {};
template <typename T_Enum>
const std::map<std::string, int> EnumMap<T_Enum>::STRING_TO_INT = {};


// Convert an enum value to a string name.
template <typename T_Enum>
T_Enum ParseValue(std::string name)
{
	// Convert name to uppercase first
	std::transform(name.begin(), name.end(), name.begin(), ::toupper);
	return EnumMap<T_Enum>::STRING_TO_VALUE.at(name);
}

// Convert an enum value to a string name.
template <typename T_Enum>
T_Enum ParseValue(std::string name)
{
	// Convert name to uppercase first
	std::transform(name.begin(), name.end(), name.begin(), ::toupper);
	return EnumMap<T_Enum>::STRING_TO_VALUE.at(name);
}

// Convert an string name to an enum value.
template <typename T_Enum>
std::string ValueName(T_Enum value)
{
	return EnumMap<T_Enum>::VALUE_TO_STRING.at(value);
}

// Return the string representation of an enum's name.
template <typename T_Enum>
std::string EnumName();

// Return the type of a tag.
Type GetTagType(GameTag tag);

std::string GetTagEnumValueName(GameTag tag, int value);


{enums_begin}
template <> class EnumMap<{enum_name}>
{
public:
	static const std::string ENUM_NAME;
	static const std::map<{enum_name}, std::string> VALUE_TO_STRING;
	static const std::map<std::string, {enum_name}> STRING_TO_VALUE;
	static const std::map<std::string, int> STRING_TO_INT;
};
{enums_end}

}; // namespace enums

#endif // _ENUMS_H_